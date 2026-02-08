"""
rewordapp.wordparser
====================

word parsing and rewriting utilities.
"""

import re
import string

import rewordapp.rewritten as rewritten

class WordParser:

    def __init__(self, text: str):
        self._text = text
        self._prefix = ""
        self._suffix = ""
        self._word = ""

        self._parse()

    # ------------------------------------------------------------
    # Magic methods
    # ------------------------------------------------------------

    def __len__(self) -> int:
        """Return 1 if word was parsed, else 0."""
        return 1 if self._word else 0

    def __bool__(self) -> bool:
        """Return True if word was parsed."""
        return bool(self._word)

    # ------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------

    @property
    def raw(self) -> str:
        return self._text

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def word(self):
        return self._word

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------

    def _parse(self) -> None:
        """Parse word from raw text."""
        punc_pattern = f"[{re.escape(string.punctuation)}]"
        pattern = rf"""(?ix)
            (?P<prefix>{punc_pattern}+)?
            (?P<word>\w+({punc_pattern}+\w+)*)
            (?P<suffix>{punc_pattern}+)?
        """

        match = re.match(pattern, self._text)
        if not match:
            return

        self._prefix = match.groupdict().get("prefix") or ""
        self._word = match.groupdict().get("word") or ""
        self._suffix = match.groupdict().get("suffix") or ""

    def generate_new(self):
        if not self:
            return self.__class__(self.raw)

        new_word = rewritten.new_word(self.word)
        return self.__class__(f"{self.prefix}{new_word}{self.suffix}")
