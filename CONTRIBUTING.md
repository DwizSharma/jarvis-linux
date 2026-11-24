# Contributing to Jarvis

Thanks for your interest in contributing! Here is everything you need to know.

---

## Setting up a development environment

```sh
git clone https://github.com/DwizSharma/jarvis-linux.git
cd jarvis-linux
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -e .
```

> `--system-site-packages` is required because `pyatspi` and `PyGObject` are
> installed as distro packages and are not available on PyPI.

---

## Project layout

```
src/jarvis/
├── app.py            CLI entry point
├── wake.py           Wake phrase loop and speech pipeline
├── commands.py       Spoken command parser
├── accessibility.py  AT-SPI desktop control
└── settings.py       Config loader
```

---

## Making changes

1. Fork the repository and create a branch off `main`:
   ```sh
   git checkout -b fix/your-fix-name
   ```
2. Make your changes. Keep each commit focused on one thing.
3. Test manually — say the wake phrase, give a command, verify the response.
4. Open a pull request against `main` with a clear description of what changed and why.

---

## Adding a new voice command

1. Add the regex pattern and handler key in `commands.py` → `run_command()`.
2. Add the spoken grammar phrase in `wake.py` → `_command_phrases()`.
3. If the command needs a new desktop action, implement it in `accessibility.py` and wire it up in `wake.py` → `_execute()`.

---

## Code style

- Follow the existing style (type hints, `from __future__ import annotations`, `LOG` for logging).
- Keep functions short and single-purpose.
- No third-party dependencies beyond `vosk` and `sounddevice` — AT-SPI bindings come from the distro.

---

## Reporting bugs

Open a GitHub Issue with:
- Your distro and desktop environment
- The command you spoke and what Jarvis said/did
- Relevant lines from `~/.local/state/jarvis/jarvis.log`
