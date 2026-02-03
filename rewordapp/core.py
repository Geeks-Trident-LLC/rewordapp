"""
rewordapp.core
==============

Core logic and shared utilities for RewordApp CE.

"""


from rewordapp.line import Line


class RewordBuilder:
    """Builds rewritten text by transforming each line according to a rule."""

    def __init__(self, text: str, rule: str = "") -> None:
        self._text = str(text)
        self._rule = rule

        # Store as list so lines can be iterated multiple times
        self._lines = [Line(line) for line in self._text.splitlines(keepends=True)]

    @property
    def raw_text(self) -> str:
        """Return the original unmodified text."""
        return self._text

    @property
    def rewritten_text(self) -> str:
        """Return the transformed text after applying rewrite rules."""
        self.apply_transform()
        parts = []
        for line in self._lines:
            parts.append(line.content)
            parts.append(line.newline)
        return "".join(parts)

    def apply_transform(self) -> None:
        """Apply rewrite rules to each line (override in subclasses)."""
        pass