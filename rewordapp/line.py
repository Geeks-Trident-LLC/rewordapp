"""
rewordapp.Line
==============

Utilities for splitting a text line into content and newline parts.

"""

import re

from rewordapp.token import build_token


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
        cursor = 0
        last_match_end = 0

        for match in re.finditer(r"\s+", self._content):
            start, end = match.start(), match.end()

            # Text before the whitespace
            segment = self._content[cursor:start]
            if segment:
                token = build_token(segment, rules=self.rules)
                tokens.append(token)

            # The whitespace itself
            ws_token = build_token(match.group(), rules=self.rules)
            tokens.append(ws_token)

            cursor = end
            last_match_end = end

        # Remaining text after the last match
        remaining = (
            self._content[last_match_end:]
            if last_match_end > 0
            else self._content
        )
        if remaining:
            final_token = build_token(remaining, rules=self.rules)
            tokens.append(final_token)

        return tokens