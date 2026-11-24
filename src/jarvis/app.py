"""Headless Jarvis desktop assistant entry point."""

from __future__ import annotations

import sys

from . import __version__
from .wake import main


def _entrypoint() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in {"--version", "-V"}:
        print(f"jarvis {__version__}")
        raise SystemExit(0)
    main()


if __name__ == "__main__":
    _entrypoint()
