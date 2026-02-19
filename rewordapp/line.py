"""
rewordapp.Line
==============

Utilities for splitting a text line into content and newline parts.

"""

import re

from rewordapp.token import build_token
from rewordapp.token import build_datetime_token

from rewordapp.rules import RewriteRules

import rewordapp.utils as utils


class Line:
    """Represents a single text line split into content and its trailing newline."""

    def __init__(self, text: str, rules=None) -> None:
        self._raw = text
        self._content = text.rstrip("\r\n")
        self._newline = text[len(self._content):]
        self._rewritten = ""
        self._unchanged = False
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
    def unchanged(self) -> bool:
        return self._unchanged

    @unchanged.setter
    def unchanged(self, value: bool) -> None:
        self._unchanged = value

    @property
    def rewritten(self) -> str:
        """Return the rewritten line content, generating it once and caching the result."""

        if self.unchanged:
            return self.content

        # Return cached value if already computed
        if self._rewritten:
            return self._rewritten

        tokens = self.tokenize()
        if not tokens:
            return ""

        self._rewritten = "".join(token.rewritten for token in tokens)
        return self._rewritten

    def tokenize(self):
        """Tokenize content, applying datetime rewrite when applicable."""
        if not self.is_nonempty:
            return []

        tokens = []

        # Determine whether datetime rewriting is available
        dt_rule = (
            self.rules.get_datetime_token_rule()
            if isinstance(self.rules, RewriteRules)
            else None
        )

        # If datetime rule exists, attempt datetime‑aware tokenization
        if dt_rule:
            parts = utils.extract_non_whitespace(self._content)
            dt_segments = dt_rule.extract_segments(parts)
            left, dt_text, right = utils.extract_segments(self._content,
                                                          dt_segments)
            dt_token = build_datetime_token(dt_text, rules=self.rules)

            if dt_token:
                # Left side
                if left:
                    for chunk in utils.split_by_matches(left, r"(?u)\s+"):
                        tokens.append(build_token(chunk, rules=self.rules))

                # Datetime token
                tokens.append(dt_token)

                # Right side
                if right:
                    for chunk in utils.split_by_matches(right, r"(?u)\s+"):
                        tokens.append(build_token(chunk, rules=self.rules))

                return tokens

        # Fallback: simple whitespace tokenization
        for chunk in utils.split_by_matches(self._content, r"(?u)\s+"):
            tokens.append(build_token(chunk, rules=self.rules))

        return tokens