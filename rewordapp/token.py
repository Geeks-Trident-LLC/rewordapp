
import re

from rewordapp.netparser import IPv4Parser, IPv6Parser, MACParser


class BaseToken:
    """Base class for text units that may match a specific token type."""

    def __init__(self, text: str, rules=None, extras=None) -> None:
        self._text = text
        self.rules = rules if isinstance(rules, dict) else {}
        self.extras = extras if isinstance(extras, list) else []

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


# ---------------------------------------------------------------------------

class FallbackToken(BaseToken):
    """Token that always matches when no other token type applies."""

    def _detect(self) -> None:
        self._matched = True


class WhitespaceToken(BaseToken):
    """Token representing a run of whitespace characters."""

    def _detect(self) -> None:
        self._matched = bool(re.fullmatch(r"\s+", self._text))


class IPv4Token(BaseToken):
    """Token representing an IPv4 address."""

    def _detect(self) -> None:
        ipv4 = IPv4Parser(self._text)
        if ipv4:
            self._matched = True
            self.parsed_node = ipv4

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
        ipv6 = IPv6Parser(self._text)
        if ipv6:
            self._matched = True
            self.parsed_node = ipv6


class MACToken(BaseToken):
    """Token representing a MAC address."""

    def _detect(self) -> None:
        mac = MACParser(self._text)
        if mac:
            self._matched = True
            self.parsed_node = mac


def build_token(
    text: str,
    rules: dict | None = None,
    extras: list | None = None,
):
    """Return the first token type that matches the given text."""
    token_types = [
        MACToken,
        IPv4Token,
        IPv6Token,
        WhitespaceToken,
    ]

    if text:
        for token_cls in token_types:
            token = token_cls(text, rules=rules, extras=extras)
            if token:
                return token

    return FallbackToken(text, rules=rules, extras=extras)


def add_token_if_new(token, collection):
    """Append the token to the collection if it is not a fallback and not already present."""
    if isinstance(token, FallbackToken):
        return

    if not collection:
        collection.append(token)
        return

    exists = any(item == token for item in collection)
    if not exists:
        collection.append(token)
