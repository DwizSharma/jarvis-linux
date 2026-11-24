"""Headless local wake phrase and speech command loop."""

from __future__ import annotations

import json
import logging
import queue
import re
import subprocess
import sys
import time
from pathlib import Path

from .accessibility import Desktop, open_app
from .commands import run_command
from .settings import Settings, load_settings

LOG = logging.getLogger("jarvis")


def main() -> None:
    settings = load_settings()
    model_path = settings.model_path
    try:
        import sounddevice as sd  # type: ignore[import-not-found]
        from vosk import KaldiRecognizer, Model, SetLogLevel  # type: ignore[import-not-found]
    except ImportError as exc:
        _notify("Install vosk and sounddevice for local voice recognition")
        raise SystemExit(1) from exc
    if not model_path.is_dir():
        _say(f"The {settings.language} speech model is missing. Run install dot sh.", settings)
        _notify(f"Jarvis Vosk model not found: {model_path}")
        raise SystemExit(1)

    state = Path.home() / ".local/state/jarvis"
    state.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=state / "jarvis.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    SetLogLevel(-1)
    model = Model(str(model_path))
    wake_phrases = _wake_phrases(settings)
    exit_phrases = _exit_phrases()
    command_phrases = _command_phrases(settings)
    # Listen for both the standalone wake word and complete one-shot commands
    # such as "Jarvis open Firefox". Vosk needs these forms in its grammar.
    inline_phrases = [f"jarvis {command}" for command in command_phrases]
    wake_recognizer = KaldiRecognizer(
        model, 16000, json.dumps(wake_phrases + exit_phrases + inline_phrases + ["[unk]"])
    )
    command_recognizer = KaldiRecognizer(model, 16000, json.dumps(command_phrases + ["[unk]"]))
    recognizer = wake_recognizer
    audio: queue.Queue[bytes] = queue.Queue(maxsize=40)

    def capture(data: bytes, frames: int, timing: object, status: object) -> None:
        if status:
            LOG.warning("Microphone status: %s", status)
        try:
            audio.put_nowait(bytes(data))
        except queue.Full:
            pass

    try:
        stream = sd.RawInputStream(
            samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=capture
        )
        stream.start()
    except Exception as exc:
        _say("Jarvis cannot access the microphone", settings)
        _notify(f"Jarvis could not access microphone: {exc}")
        raise SystemExit(1) from exc

    LOG.info("Listening in %s mode for %r", settings.language, settings.wake_phrase)
    ready = {"hindi": "जार्विस तैयार है", "hinglish": "Jarvis tayyar hai"}.get(settings.language, "Jarvis is ready")
    _say(ready, settings)
    mode = "wake"
    command_deadline = 0.0
    desktop: Desktop | None = None
    try:
        while True:
            try:
                chunk = audio.get(timeout=0.5)
            except queue.Empty:
                if mode == "command" and time.monotonic() > command_deadline:
                    timeout_message = "Command nahi mila. Main sun raha hoon." if settings.language != "english" else "I did not hear a command. Going back to sleep."
                    _say(timeout_message, settings)
                    _flush(audio)
                    recognizer.Reset()
                    mode = "wake"
                    recognizer = wake_recognizer
                continue

            if not recognizer.AcceptWaveform(chunk):
                continue
            phrase = json.loads(recognizer.Result()).get("text", "").strip()
            if not phrase:
                continue
            LOG.info("Recognized (%s): %s", mode, phrase)
            normalized = _normalize(phrase)
            if any(_normalize(item) in normalized for item in exit_phrases):
                _say("Theek hai, Jarvis band ho raha hai." if settings.language != "english" else "Okay, Jarvis is shutting down.", settings)
                LOG.info("Exit phrase received")
                return
            if mode == "command" and _normalize(phrase) in {
                "yes", "yeah", "yep", "okay", "ok", "ji", "ji boliye",
                "haan", "han", "हाँ", "हां", "बोलिए", "बोलिये", "unk",
            }:
                # Ignore the assistant's spoken acknowledgement if the
                # microphone hears it acoustically as an utterance.
                command_deadline = time.monotonic() + 12
                continue
            if mode == "wake":
                inline_command = re.sub(r"^jarvis\b\s*", "", phrase, count=1, flags=re.I).strip()
                if inline_command != phrase.strip() and inline_command:
                    desktop = _execute(inline_command, desktop, settings)
                    _flush(audio)
                    recognizer.Reset()
                    continue
                if not any(_normalize(item) in normalized for item in wake_phrases):
                    continue
                mode = "command"
                command_deadline = time.monotonic() + 12
                recognizer = command_recognizer
                recognizer.Reset()
                _say("Ji, boliye" if settings.language != "english" else "Yes?", settings)
                _flush(audio)
            else:
                if _normalize(phrase) in {"cancel", "never mind", "stop listening", "रद्द करो", "cancel karo"}:
                    mode = "wake"
                    recognizer = wake_recognizer
                    recognizer.Reset()
                    _say("Okay", settings)
                    _flush(audio)
                    continue
                desktop = _execute(phrase, desktop, settings)
                mode = "wake"
                recognizer = wake_recognizer
                recognizer.Reset()
                _flush(audio)
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()
        stream.close()


def _wake_phrases(settings: Settings) -> list[str]:
    phrases = [settings.wake_phrase]
    if settings.language in {"english", "hinglish"}:
        phrases.extend(["wake up jarvis", "wake up marvis", "wake up top is", "wake jarvis", "hey jarvis"])
    if settings.language in {"hindi", "hinglish"}:
        phrases.extend(["जार्विस जागो", "जागो जार्विस", "जार्विस उठो", "jarvis jaago", "jaago jarvis"])
    return list(dict.fromkeys(phrase for phrase in phrases if phrase))


def _exit_phrases() -> list[str]:
    return [
        "jarvis soja bete", "soja bete", "so ja bete", "so jao jarvis",
        "jarvis top ja", "top ja", "jarvis exit", "exit jarvis",
    ]


def _command_phrases(settings: Settings) -> list[str]:
    phrases = [
        "list controls", "show controls", "show elements", "controls dikhao",
        "jarvis soja bete", "soja bete", "so ja bete", "so jao jarvis",
        "jarvis top ja", "top ja", "exit jarvis",
        "screenshot", "take screenshot", "screenshot lo", "स्क्रीनशॉट लो",
        "scroll up", "scroll down", "upar scroll", "neeche scroll",
        "ऊपर स्क्रॉल", "नीचे स्क्रॉल", "ऊपर स्क्रॉल करो", "नीचे स्क्रॉल करो",
        "open firefox", "open chrome", "open calculator", "open terminal",
        "open files", "open browser", "launch firefox", "launch calculator",
        "open [unk]", "launch [unk]", "[unk] kholo", "[unk] खोलो", "खोलो [unk]",
        "click [unk]", "activate [unk]", "[unk] par click karo", "[unk] पर क्लिक करो",
        "type [unk] into [unk]", "enter [unk] in [unk]", "[unk] में [unk] लिखो",
        "controls दिखाओ", "कंट्रोल दिखाओ", "[unk]",
    ]
    if settings.language in {"hindi", "hinglish"}:
        phrases.extend(["ओपन [unk]", "[unk] में [unk] लिखो", "[unk] पर क्लिक करो"])
    return list(dict.fromkeys(phrases))


def _normalize(text: str) -> str:
    return re.sub(r"[^\w ]", "", text.casefold()).strip()


def _execute(command: str, desktop: Desktop | None, settings: Settings) -> Desktop | None:
    try:
        if desktop is None:
            desktop = Desktop()
        handler = lambda target, value: desktop.type_text(target, value)
        response = run_command(command, {
            "open": open_app,
            "click": desktop.click,
            "type": handler,
            "type_hi": handler,
            "scroll": desktop.scroll,
            "screenshot": lambda _unused: desktop.screenshot(),
            "list": lambda _unused: _list_controls(desktop),
        })
    except Exception as exc:
        response = f"I could not do that: {exc}"
    LOG.info("Command result: %s", response)
    _say(_translate_response(response, settings.language)[:240], settings)
    return desktop


def _list_controls(desktop: Desktop) -> str:
    items = desktop.elements()
    if not items:
        return "No accessible controls found. Check desktop accessibility settings."
    return "Available controls: " + ", ".join(item.name for item in items[:8])


def _translate_response(response: str, language: str) -> str:
    if language == "english":
        return response
    if response.startswith("Opened "):
        return response.removeprefix("Opened ").removesuffix(".") + " khol diya."
    if response.startswith("Activated "):
        return response.removeprefix("Activated ").removesuffix(".") + " par click kar diya."
    if response.startswith("Typed into "):
        return response.removeprefix("Typed into ").removesuffix(".") + " mein likh diya."
    if response.startswith("Scrolled down"):
        return "Neeche scroll kar diya."
    if response.startswith("Scrolled up"):
        return "Upar scroll kar diya."
    if response.startswith("Screenshot saved to "):
        return "Screenshot save kar diya."
    return response


def _flush(audio: queue.Queue[bytes]) -> None:
    while True:
        try:
            audio.get_nowait()
        except queue.Empty:
            return


def _say(message: str, settings: Settings) -> None:
    """Speak with a slower, lower-pitched local male voice."""
    try:
        subprocess.run(
            ["spd-say", "-w", "-l", settings.speech_language, "-t", settings.variant,
             "-r", str(settings.rate), "-p", str(settings.pitch), message],
            timeout=20,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        LOG.info("Speech output unavailable: %s", message)


def _notify(message: str) -> None:
    try:
        subprocess.Popen(["notify-send", "Jarvis", message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        LOG.error(message)


if __name__ == "__main__":
    main()
