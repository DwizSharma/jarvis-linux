"""Small, explicit command parser for desktop actions."""

from __future__ import annotations

import re
from collections.abc import Callable


Handler = Callable[..., str]


def run_command(text: str, handlers: dict[str, Handler]) -> str:
    command = text.strip()
    patterns: list[tuple[str, str]] = [
        (r"^(?:open|launch|khol|kholo|खोलो|खोलिए)\s+(.+)$", "open"),
        (r"^(.+?)\s+(?:khol(?:o)?(?:\s+do)?|kholo|खोलो|खोल दो|खोलिए)$", "open"),
        (r"^(?:click|activate|click karo|click kar|क्लिक करो|क्लिक कर)\s+(.+)$", "click"),
        (r"^(.+?)\s+(?:par click karo|par click kar|पर क्लिक करो|पर क्लिक कर)$", "click"),
        (r"^(?:type|enter)\s+(.+?)\s+(?:into|in)\s+(.+)$", "type"),
        (r"^(.+?)\s+(?:mein|में)\s+(.+?)\s+(?:likho|लिखो)$", "type_hi"),
        (r"^(?:scroll|स्क्रॉल)\s+(up|down|upar|neeche|ऊपर|नीचे)$", "scroll"),
        (r"^(?:upar|ऊपर)\s+(?:scroll|स्क्रॉल)(?:\s+karo|\s+करो)?$", "scroll_up"),
        (r"^(?:neeche|नीचे)\s+(?:scroll|स्क्रॉल)(?:\s+karo|\s+करो)?$", "scroll_down"),
    ]
    if re.fullmatch(r"(?:take )?screenshot|screenshot (?:lo|le lo)|स्क्रीनशॉट लो", command, re.I):
        return handlers["screenshot"]("")
    if re.fullmatch(r"controls?|(?:show|list)\s+(?:accessible )?(?:elements|controls)|(?:controls|control) (?:dikhao|dikhaao)|कंट्रोल दिखाओ", command, re.I):
        return handlers["list"]("")
    for pattern, key in patterns:
        match = re.match(pattern, command, re.I)
        if match:
            if key == "type":
                return handlers[key](match.group(2), match.group(1))  # type: ignore[call-arg]
            if key == "type_hi":
                return handlers[key](match.group(1), match.group(2))  # type: ignore[call-arg]
            if key == "scroll_up":
                return handlers["scroll"]("up")
            if key == "scroll_down":
                return handlers["scroll"]("down")
            if key == "scroll":
                direction = {"upar": "up", "ऊपर": "up", "neeche": "down", "नीचे": "down"}.get(match.group(1).casefold(), match.group(1).casefold())
                return handlers["scroll"](direction)
            return handlers[key](match.group(1))
    return "Try: open Firefox, click Search, type hello into Search, scroll down, screenshot, or list controls."
