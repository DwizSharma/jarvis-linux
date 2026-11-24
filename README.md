# 🤖 Jarvis for Linux

> A headless, fully offline, voice-controlled desktop assistant for Linux — no cloud, no tracking, no window.

![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/platform-Linux-orange?logo=linux)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

Jarvis runs as a lightweight background process. It listens locally for a wake phrase, understands spoken commands, and operates your desktop through the **AT-SPI accessibility bus** — no screen coordinates, no simulated mouse clicks, no proprietary APIs.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎙️ Offline speech recognition | Powered by [Vosk](https://alphacephei.com/vosk/) — your voice never leaves your machine |
| 🌐 Multilingual | English, Hindi, and Hinglish (Indian-English) |
| 🔊 Voice feedback | Spoken replies via [Speech Dispatcher](https://freebsoft.org/speechd) |
| 🖥️ Desktop control | Open apps, click controls, type text, scroll — all through AT-SPI |
| 📸 Screenshots | Auto-detects and uses your installed screenshot tool |
| 🔁 Auto-start | Registers a freedesktop autostart entry at login |
| ⚙️ Configurable | Voice variant, speed, pitch, wake phrase — all in a single TOML file |

---

## 🏗️ Architecture

```
src/jarvis/
├── app.py            Entry point
├── wake.py           Wake phrase loop and speech command pipeline
├── commands.py       Spoken command parser (English + Hindi patterns)
├── accessibility.py  AT-SPI desktop control — apps, clicks, text, scroll, screenshots
└── settings.py       Config loader (TOML) with sane defaults
```

Jarvis has no GUI. It lives in your session, stays silent until it hears the wake phrase, then acts on a single spoken command and goes back to sleep.

---

## 📋 Requirements

- Linux desktop with AT-SPI enabled (GNOME, Cinnamon, XFCE, KDE, etc.)
- Python 3.11+
- Working microphone + PortAudio
- `speech-dispatcher` for voice output
- One screenshot tool: `gnome-screenshot`, `xfce4-screenshooter`, `scrot`, or `grim`

**Debian / Ubuntu:**

```sh
sudo apt install python3-gi gir1.2-atspi-2.0 python3-pyatspi \
    portaudio19-dev speech-dispatcher gnome-screenshot unzip curl
```

---

## 🚀 Install

```sh
git clone https://github.com/DwizSharma/jarvis-linux.git
cd jarvis-linux
./install.sh
```

The installer:
1. Creates a `.venv` with access to system AT-SPI bindings
2. Installs `vosk` and `sounddevice`
3. Downloads the English, Hindi, and Indian-English Vosk models into `~/.local/share/jarvis/`
4. Copies the example config to `~/.config/jarvis/config.toml`
5. Registers a freedesktop autostart entry so Jarvis starts at login

Then either log out and back in, or start Jarvis now:

```sh
./run-jarvis
```

Jarvis speaks **"Jarvis is ready"** when it's listening.

---

## 🗣️ Voice Commands

Give Jarvis a command either in one sentence or in two steps. For one sentence,
start with **"Jarvis"** and follow it with the command, such as **"Jarvis open Firefox"**.
You can also say the configured wake phrase, wait for **"Yes?"**, and then give
the command.

| Command | Example |
|---|---|
| Open an app | `"open Calculator"` / `"launch Firefox"` |
| Click a control | `"click Search"` |
| Type into a field | `"type hello there into Message"` |
| Scroll | `"scroll down"` / `"scroll up"` |
| Take a screenshot | `"take screenshot"` |
| List controls | `"list controls"` |
| Cancel | `"cancel"` / `"never mind"` |
| Exit Jarvis | `"Jarvis soja bete"` |

Hindi examples: `"कैलकुलेटर खोलो"`, `"नीचे स्क्रॉल करो"`, `"स्क्रीनशॉट लो"`

---

## ⚙️ Configuration

Edit `~/.config/jarvis/config.toml`:

```toml
[voice]
language    = "english"       # english | hindi | hinglish
variant     = "male2"         # male1 | male2 | male3
rate        = -12             # speech rate  (-50 to 50)
pitch       = -18             # voice pitch  (-50 to 50)
wake_phrase = "wake up jarvis"
```

Restart Jarvis after changes. For Hindi mode, set `wake_phrase = "जार्विस जागो"`.

---

## 🛑 Stop / Disable

| Action | How |
|---|---|
| Stop the current process | Say `"Jarvis soja bete"` or kill the `jarvis.app` process |
| Disable autostart | `rm ~/.config/autostart/jarvis.desktop` |

---

## 🔒 Privacy

All speech recognition runs locally using Vosk models stored in `~/.local/share/jarvis/`. No audio is ever sent to a server.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss any significant change.

1. Fork the repository
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit your changes
4. Open a pull request

---

## 📄 License

MIT — see [LICENSE](LICENSE).
