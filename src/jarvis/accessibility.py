"""Linux desktop controls backed by the AT-SPI accessibility bus."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Any


class AccessibilityUnavailable(RuntimeError):
    pass


def _load_atspi() -> Any:
    """Load distro-provided PyGObject/pyatspi without assuming a pip install."""
    try:
        import pyatspi  # type: ignore[import-not-found]
        return pyatspi
    except ImportError as exc:
        raise AccessibilityUnavailable(
            "AT-SPI bindings are missing. Install python3-pyatspi and enable "
            "accessibility in your desktop settings."
        ) from exc


@dataclass
class Element:
    name: str
    role: str
    path: str
    obj: Any


class Desktop:
    """Query and operate accessible UI elements through AT-SPI."""

    def __init__(self) -> None:
        self.atspi = _load_atspi()

    def elements(self, query: str = "") -> list[Element]:
        desktop = self.atspi.Registry.getDesktop(0)
        found: list[Element] = []

        def visit(node: Any, path: str, depth: int = 0) -> None:
            if depth > 40:
                return
            try:
                name = (node.name or "").strip()
                role = node.getRoleName() or "unknown"
                if name and (not query or query.casefold() in name.casefold()):
                    found.append(Element(name, role, path, node))
                for index in range(node.childCount):
                    visit(node.getChildAtIndex(index), f"{path}/{index}", depth + 1)
            except Exception:
                return

        for index in range(desktop.childCount):
            visit(desktop.getChildAtIndex(index), str(index))
        return found

    def click(self, query: str) -> str:
        element = self._one(query)
        actions = element.obj.queryAction()
        for index in range(actions.nActions):
            action = actions.getActionName(index).casefold()
            if action in {"click", "press", "activate", "toggle"}:
                actions.doAction(index)
                return f"Activated {element.name}."
        raise RuntimeError(f"{element.name!r} has no accessible activation action.")

    def type_text(self, query: str, value: str) -> str:
        element = self._one(query)
        try:
            text = element.obj.queryEditableText()
            text.setTextContents(value)
            return f"Typed into {element.name}."
        except Exception:
            try:
                value_iface = element.obj.queryValue()
                value_iface.currentValue = float(value)
                return f"Set {element.name}."
            except Exception as exc:
                raise RuntimeError(f"{element.name!r} cannot accept text through AT-SPI.") from exc

    def scroll(self, direction: str) -> str:
        desktop = self.atspi.Registry.getDesktop(0)
        # AT-SPI exposes scrolling as component actions on many toolkits.
        choices = {"down": ("scroll down", "scroll_down"), "up": ("scroll up", "scroll_up")}
        names = choices[direction]
        for element in self.elements():
            try:
                actions = element.obj.queryAction()
                for index in range(actions.nActions):
                    if actions.getActionName(index).casefold() in names:
                        actions.doAction(index)
                        return f"Scrolled {direction}."
            except Exception:
                continue
        # Fall back to focused-window keyboard scrolling, still through AT-SPI
        # key synthesis, never raw X11 pointer coordinates.
        try:
            self.atspi.Registry.generateKeyboardEvent(
                0, "Page_Down" if direction == "down" else "Page_Up", self.atspi.KEY_SYM
            )
            return f"Scrolled {direction} by one page."
        except Exception as exc:
            raise RuntimeError("No accessible scroll action was available.") from exc

    def screenshot(self) -> str:
        """Use the desktop's screenshot portal/tool; return the saved path."""
        from datetime import datetime
        from pathlib import Path

        folder = Path.home() / "Pictures" / "Jarvis"
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / f"screen-{datetime.now():%Y%m%d-%H%M%S}.png"
        candidates = [["gnome-screenshot", "-f", str(target)], ["xfce4-screenshooter", "-f", "-s", str(target)], ["scrot", str(target)], ["grim", str(target)]]
        for command in candidates:
            if not shutil_which(command[0]):
                continue
            result = subprocess.run(command, capture_output=True, text=True, timeout=20)
            if result.returncode == 0 and target.exists():
                return f"Screenshot saved to {target}."
            detail = result.stderr.strip()
            if detail:
                raise RuntimeError(detail)
        raise RuntimeError("Install a screenshot utility (gnome-screenshot, scrot, or grim).")

    def _one(self, query: str) -> Element:
        matches = self.elements(query)
        if not matches:
            raise RuntimeError(f"No accessible element matched {query!r}.")
        if len(matches) > 1:
            choices = ", ".join(f"{item.name} ({item.role})" for item in matches[:5])
            raise RuntimeError(f"More than one element matched. Be more specific: {choices}")
        return matches[0]


def shutil_which(command: str) -> str | None:
    from shutil import which
    return which(command)


def open_app(query: str) -> str:
    """Launch an installed desktop application by its visible application name."""
    try:
        from gi.repository import Gio  # type: ignore[import-not-found]
    except ImportError as exc:
        raise AccessibilityUnavailable("Install python3-gi to open apps via the desktop application registry.") from exc
    apps = Gio.AppInfo.get_all()
    matches = [app for app in apps if query.casefold() in app.get_display_name().casefold()]
    if not matches:
        raise RuntimeError(f"No installed app matched {query!r}.")
    if len(matches) > 1:
        names = ", ".join(app.get_display_name() for app in matches[:5])
        raise RuntimeError(f"Multiple apps matched; use a more specific name: {names}")
    matches[0].launch([], None)
    return f"Opened {matches[0].get_display_name()}."

