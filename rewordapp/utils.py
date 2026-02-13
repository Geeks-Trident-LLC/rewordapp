"""
rewordapp.utils
---------------

General-purpose utility functions used across RewordApp.
"""

import re


def split_by_matches(text, pattern=r"\s+"):
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
