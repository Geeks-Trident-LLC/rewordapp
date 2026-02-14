"""
rewordapp.utils
---------------

General-purpose utility functions used across RewordApp.
"""

import re


def split_by_matches(text, pattern=r"(?u)\s+"):
    """Split text into alternating segments of non-matching and matching substrings."""
    parts = []
    last_end = 0

    for m in re.finditer(pattern, text):
        if m.start() > last_end:
            parts.append(text[last_end:m.start()])
        parts.append(m.group())
        last_end = m.end()

    if last_end < len(text):
        parts.append(text[last_end:])

    return parts


def extract_non_whitespace(text: str) -> list[str]:
    """Return all contiguous non‑whitespace segments from the text."""
    return re.findall(r"(?u)\S+", text)
