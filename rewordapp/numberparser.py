"""
rewordapp.numberparser
===================

number parsing and rewriting utilities.
"""

import re

import rewordapp.rewritten as rewritten

class NumberParser:

    def __init__(self, text: str):
        self._text = text
        self._prefix = ""
        self._suffix = ""
        self._number = ""

        self._parse()

    # ------------------------------------------------------------
    # Magic methods
    # ------------------------------------------------------------

    def __len__(self) -> int:
        """Return 1 if number was parsed, else 0."""
        return 1 if self._number else 0

    def __bool__(self) -> bool:
        """Return True if number was parsed."""
        return bool(self._number)

    # ------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------

    @property
    def raw_text(self) -> str:
        return self._text

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def number(self):
        return self._number

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------

    def _parse(self) -> None:
        """Parse number from raw text."""
        pattern = r"""(?ix)
            (?P<prefix>[^\w\s]+?)?
            (?P<number>
                (\d+[.]\d+)|
                ([.]\d+)|
                (\d+[.])|
                \d+
            )
            (?P<suffix>[^\w\s]+?)?
        """

        match = re.match(pattern, self._text)
        if not match:
            return

        self._prefix = match.groupdict().get("prefix", "")
        self._number = match.groupdict().get("number", "")
        self._suffix = match.groupdict().get("suffix", "")

    def generate_new(self):
        if not self:
            return self.__class__(self.raw_text)

        new_number = rewritten.new_number(self.number)
        return self.__class__(f"{self.prefix}{new_number}{self.suffix}")
