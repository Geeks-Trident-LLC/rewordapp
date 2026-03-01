"""
rewordapp.core.token
====================

This module provides the core token classes used to detect, classify,
and transform segments of text during rewriting.
"""


import re

from rewordapp.parser.net import IPv4Parser, IPv6Parser, MACParser
from rewordapp.parser.url import URLParser
from rewordapp.parser.number import NumberParser
from rewordapp.parser.word import WordParser
from rewordapp.parser.fperm import FilePermissionParser
from rewordapp.parser.datetime import DateTimeParser
from rewordapp.parser.datetime import DateParser

from rewordapp.rules import RewriteRules


class BaseToken:
    """Base class for text units that may match a specific token type."""

    def __init__(self, text: str, rules=None) -> None:
        self._text = text
        self.rules = rules if isinstance(rules, RewriteRules) else RewriteRules()

        self._masked = ""
        self._rewritten = ""
        self._matched = False
        self.parsed_node = None  # Parsed object (IPv4, IPv6, MAC, etc.)

        self._process()

    def __len__(self) -> int:
        return 1 if self._matched else 0

    def __bool__(self) -> bool:
        return self._matched

    def __eq__(self, other) -> bool:
        if type(self).__name__ == type(other).__name__:
            if hasattr(self.parsed_node, "value"):
                return self.parsed_node.value == other.parsed_node.value
            return self.raw == other.raw
        return False

    def __ne__(self, other) -> bool:
        if type(self).__name__ == type(other).__name__:
            if hasattr(self.parsed_node, "value"):
                return self.parsed_node.value != other.parsed_node.value
            return self.raw != other.raw
        return False

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def raw(self) -> str:
        """Return the original text."""
        return self._text

    @property
    def mask(self) -> str:
        """Return the masked representation."""
        return self._masked

    @property
    def rewritten(self) -> str:
        """Return the rewritten representation."""
        if not self:
            return ""

        if isinstance(self.parsed_node, str):
            return self.parsed_node

        has_rule = self.rules.has_rule_for(self)

        if has_rule:
            # Boolean rule: True → rewrite, False → keep original
            if self.rules.has_boolean_rule(self):
                if self.rules.get_rule_for(self):
                    self._rewritten = self.parsed_node.generate_new().raw
                else:
                    self._rewritten = self.parsed_node.raw
            else:
                # Non-boolean rule → always rewrite
                self._rewritten = self.parsed_node.generate_new().raw
        else:
            # No rule yet → rewrite and register rule
            self._rewritten = self.parsed_node.generate_new().raw
            self.rules.update_rule_for(self)

        return self._rewritten

    # --- Processing pipeline -------------------------------------------------

    def _process(self) -> None:
        """Run token‑specific detection and transformation."""
        self._detect()
        self._apply_rewrite()
        self._apply_mask()

    def _detect(self) -> None:
        """Determine whether this text matches the token type."""
        # Default: never matches
        pass

    def _apply_rewrite(self) -> None:
        """Compute rewritten form (default: unchanged)."""
        self._rewritten = self._text

    def _apply_mask(self) -> None:
        """Compute masked form (default: unchanged)."""
        self._masked = self._text

    def _update_parsed_node(self, parser_cls) -> None:
        """Instantiate and store a parsed node, marking it as matched when appropriate."""
        node = parser_cls(self._text)
        if node:
            self.parsed_node = node
            self._matched = True


# ---------------------------------------------------------------------------

class FallbackToken(BaseToken):
    """Token that always matches when no other token type applies."""

    def _detect(self) -> None:
        self._matched = True
        self.parsed_node = self._text


class WhitespaceToken(BaseToken):
    """Token representing a run of whitespace characters."""

    def _detect(self) -> None:
        self._matched = bool(re.fullmatch(r"\s+", self._text))
        self.parsed_node = self._text


class IPv4Token(BaseToken):
    """Token representing an IPv4 address."""

    def _detect(self) -> None:
        self._update_parsed_node(IPv4Parser)

    def __eq__(self, other):
        if isinstance(other, IPv4Token):
            return self.parsed_node.value == other.parsed_node.value
        return False

    def __ne__(self, other):
        if isinstance(other, IPv4Token):
            return self.parsed_node.value != other.parsed_node.value
        return False

class IPv6Token(BaseToken):
    """Token representing an IPv6 address."""

    def _detect(self) -> None:
        self._update_parsed_node(IPv6Parser)


class MACToken(BaseToken):
    """Token representing a MAC address."""

    def _detect(self) -> None:
        self._update_parsed_node(MACParser)


class URLToken(BaseToken):
    """Token representing a URL."""
    def _detect(self) -> None:
        self._update_parsed_node(URLParser)


class NumberToken(BaseToken):
    """Token representing a number."""
    def _detect(self) -> None:
        self._update_parsed_node(NumberParser)


class WordToken(BaseToken):
    """Token representing a word."""
    def _detect(self) -> None:
        self._update_parsed_node(WordParser)


class FilePermissionToken(BaseToken):
    """Token representing a file permission."""
    def _detect(self) -> None:
        self._update_parsed_node(FilePermissionParser)


class DateTimeToken(BaseToken):

    @property
    def rewritten(self):
        if not self:
            return self.raw
        dt_token_rule = self.rules.get_datetime_token_rule()
        if dt_token_rule:
            if dt_token_rule.is_rewrite:
                self._rewritten = self.parsed_node.rewritten
                return self._rewritten
            else:
                return self.raw
        return self.raw

    """Token representing a datetime."""
    def _detect(self) -> None:
        self._update_parsed_node(DateTimeParser)
        if not self:
            self._update_parsed_node(DateParser)


def build_token(text: str, rules: dict | None = None):
    """Return the first token type that matches the given text."""
    token_types = [
        FilePermissionToken,
        URLToken,
        MACToken,
        IPv6Token,
        IPv4Token,
        NumberToken,
        WordToken,
        WhitespaceToken,
    ]

    if text:
        for token_cls in token_types:
            token = token_cls(text, rules=rules)
            if token:
                return token

    return FallbackToken(text, rules=rules)


def build_fallback_token(text: str):
    """Create and return a fallback token for unmatched input."""
    return FallbackToken(text)


def build_datetime_token(text: str, rules: dict | None = None):
    """Create and return a datetime token for matched input."""
    return DateTimeToken(text, rules=rules)
