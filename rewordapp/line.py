"""
rewordapp.Line
==============

Utilities for splitting a text line into content and newline parts.

"""


class Line:
    """Represents a single text line split into content and its trailing newline."""

    def __init__(self, text: str) -> None:
        self._raw = text
        self._content = text.rstrip("\r\n")
        self._newline = text[len(self._content):]

    @property
    def raw(self) -> str:
        """Return the original unmodified line."""
        return self._raw

    @property
    def content(self) -> str:
        """Return the line content without trailing newline characters."""
        return self._content

    @property
    def newline(self) -> str:
        """Return the trailing newline characters (if any)."""
        return self._newline

    @property
    def rewritten(self) -> str:
        """Return the rewritten line content (defaults to original content)."""
        return self._content

