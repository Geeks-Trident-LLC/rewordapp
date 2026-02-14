"""
rewordapp.Line
==============

Utilities for splitting a text line into content and newline parts.

"""

import re

from rewordapp.token import build_token

import rewordapp.utils as utils


class Line:
    """Represents a single text line split into content and its trailing newline."""

    def __init__(self, text: str, rules=None) -> None:
        self._raw = text
        self._content = text.rstrip("\r\n")
        self._newline = text[len(self._content):]
        self._rewritten = ""
        self.rules = rules if isinstance(rules, dict) else {}

    @property
    def raw(self) -> str:
        """Return the original unmodified line."""
        return self._raw

    @property
    def content(self) -> str:
        """Return the line content without trailing newline characters."""
        return self._content

    @property
    def length(self):
        """Return the length of the line."""
        return len(self._content)

    @property
    def is_nonempty(self):
        """Return True if the line has data."""
        return bool(re.sub(r"\s+", "", self._content))

    @property
    def newline(self) -> str:
        """Return the trailing newline characters (if any)."""
        return self._newline

    @property
    def rewritten(self) -> str:
        """Return the rewritten line content, generating it once and caching the result."""
        # Return cached value if already computed
        if self._rewritten:
            return self._rewritten

        tokens = self.tokenize()
        if not tokens:
            return ""

        self._rewritten = "".join(token.rewritten for token in tokens)
        return self._rewritten

    def tokenize(self):
        """Split content into tokens and update the token registry."""

        if not self.is_nonempty:
            return []

        tokens = []

        parts = utils.split_by_matches(self._content, r"(?u)\s+")
        for part in parts:
            token = build_token(part, rules=self.rules)
            tokens.append(token)

        return tokens