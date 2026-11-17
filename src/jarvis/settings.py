"""Small user configuration for speech language and voice style."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


MODELS = {
    "english": "vosk-model-small-en-us-0.15",
    "hindi": "vosk-model-small-hi-0.22",
    "hinglish": "vosk-model-small-en-in-0.4",
}


@dataclass(frozen=True)
class Settings:
    language: str = "english"
    variant: str = "male2"
    rate: int = -12
    pitch: int = -18
    wake_phrase: str = "wake up jarvis"

    @property
    def model_path(self) -> Path:
        override = os.environ.get("JARVIS_VOSK_MODEL")
        if override:
            return Path(override).expanduser()
        return Path.home() / ".local/share/jarvis" / MODELS[self.language]

    @property
    def speech_language(self) -> str:
        return "hi" if self.language == "hindi" else "en-US"


def load_settings() -> Settings:
    path = Path.home() / ".config/jarvis/config.toml"
    try:
        raw = tomllib.loads(path.read_text()) if path.exists() else {}
        values = raw.get("voice", {})
    except (OSError, tomllib.TOMLDecodeError):
        values = {}
    language = str(values.get("language", "english")).casefold()
    if language not in MODELS:
        language = "english"
    variant = str(values.get("variant", "male2"))
    if variant not in {"male1", "male2", "male3"}:
        variant = "male2"
    try:
        rate = max(-50, min(50, int(values.get("rate", -12))))
        pitch = max(-50, min(50, int(values.get("pitch", -18))))
    except (ValueError, TypeError):
        rate, pitch = -12, -18
    default_wake = "जार्विस जागो" if language == "hindi" else "wake up jarvis"
    wake_phrase = str(values.get("wake_phrase", default_wake)).strip() or default_wake
    return Settings(language, variant, rate, pitch, wake_phrase)
