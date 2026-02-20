"""
rewordapp.core
==============

Core logic and shared utilities for RewordApp CE.

"""


from rewordapp.line import Line

from rewordapp.rules import RewriteRules


class RewordBuilder:
    """Builds rewritten text by transforming each line according to a rule."""

    def __init__(
            self,
            text: str = "",
            data_file: str = "",
            rule_text: str = "",
            rule_file: str = "",
    ) -> None:
        """Initialize the text source and load rewrite rules."""

        if data_file:
            with open(data_file, "r", encoding="utf-8") as fh:
                self._text = fh.read()
        else:
            self._text = str(text)

        self.rules = RewriteRules(
            rule_text=rule_text,
            rule_file=rule_file,
        )

        # Store as list so lines can be iterated multiple times
        self._lines = [
            Line(line, rules=self.rules)
            for line in self._text.splitlines(keepends=True)
        ]

    def __bool__(self) -> bool:
        """Return True if the object is valid."""
        return True if self.raw.strip() else False

    def __len__(self) -> int:
        return 1 if self.raw.strip() else 0

    @property
    def raw(self) -> str:
        """Return the original unmodified text."""
        return self._text

    @property
    def line_count(self) -> int:
        """Return the number of lines contained in this object."""
        return len(self._lines)

    @property
    def rewritten(self) -> str:
        """Return the transformed text after applying rewrite rules."""
        if self.line_count == 0:
            return ""

        self.rules.refresh()

        unchanged_rule = self.rules.get_unchanged_lines_rule()
        if unchanged_rule:
            unchanged_rule.apply_unchanged_lines(self._lines)

        parts = []
        for line in self._lines:
            parts.append(line.rewritten)
            parts.append(line.newline)
        return "".join(parts)
