# Changelog

All notable changes to Jarvis are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

## [0.1.0] — 2026-11-17

### Added
- Headless voice loop with Vosk offline speech recognition (English, Hindi, Hinglish).
- Wake phrase detection; configurable phrase via `~/.config/jarvis/config.toml`.
- AT-SPI desktop control: open apps, click controls, type text, scroll, take screenshots.
- Speech Dispatcher voice feedback with configurable voice variant, rate, and pitch.
- Inline one-shot commands — say `"Jarvis open Firefox"` without the two-step wake flow.
- `--version` / `-V` flag on the `jarvis` CLI entry point.
- Freedesktop autostart entry created by `install.sh` for login auto-start.
- AT-SPI tree traversal budget to prevent freezing on large accessibility trees.
- Exit phrases in English and Hindi/Hinglish (`"jarvis soja bete"`, `"jarvis top ja"`).
