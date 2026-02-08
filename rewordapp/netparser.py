"""
rewordapp.netparser
===================

Network parsing utilities for RewordApp.

"""

import re
import ipaddress

import rewordapp.rewritten as rewritten
from rewordapp.deps import genericlib_DotObject as DotObject


def is_valid_network(network: str) -> bool:
    """
    Validate whether a string is a valid IPv4 or IPv6 network address,
    including optional subnet length.
    """
    try:
        # Split into network address and optional subnet
        address, *parts = re.split(r"[%/]", network, maxsplit=2)
        subnet = parts[0] if parts else None

        net = ipaddress.ip_network(address)
        # No subnet provided → valid
        if subnet is None:
            return True

        # Check subnet length based on IP version
        if subnet.isdigit():
            length = int(subnet)
            return (1 <= length <= 32) if net.version == 4 else (1 <= length <= 128)

        return False
    except ValueError:
        return False


class NetworkParser:
    """
    Extract and store IPv4/IPv6 network details from raw input text.
    """

    def __init__(self, text: str):
        self._text = text
        self.info = DotObject(
            network="",
            address="",
            subnet="",
            value=0,
        )
        self._prefix = ""
        self._suffix = ""
        self._parse()

    def __len__(self) -> int:
        """Return 1 if a network was parsed, else 0."""
        return 1 if self.info.network else 0

    def __bool__(self) -> bool:
        """Return True if a network was parsed, else False."""
        return bool(self.info.network)

    # --- Properties ---
    @property
    def raw_text(self) -> str:
        return self._text

    @property
    def prefix(self) -> str:
        return self._prefix or ""

    @property
    def suffix(self) -> str:
        return self._suffix or ""

    @property
    def network(self) -> str:
        return self.info.network or ""

    @property
    def address(self) -> str:
        return self.info.address or ""

    @property
    def subnet(self) -> str:
        return self.info.subnet or ""

    @property
    def value(self):
        return self.info.value or 0

    # --- Internal helpers ---
    def _match_regex(self, pattern: str) -> tuple[bool, dict]:
        """Try matching the raw text against a regex pattern."""
        match = re.match(pattern, self._text)
        return (True, match.groupdict()) if match else (False, {})

    def _apply_parsed_fields(self, parsed: dict) -> None:
        """Update info fields from regex results."""
        self.info.address = parsed.get("address", "")
        if self.info.address:
            self.info.network = parsed.get("network", "")
            addr = ipaddress.ip_address(self.info.address)
            self.info.update(value=int(addr))
            self.info.subnet = parsed.get("subnet", "")
            self._prefix = parsed.get("prefix", "") or ""
            self._suffix = parsed.get("suffix", "") or ""

    def _parse(self) -> None:
        """Base class requiring subclasses to implement `_parse`."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the `_parse` method."
        )


class IPv4Parser(NetworkParser):
    """Parser for IPv4 addresses with utilities for netmask validation and regeneration."""

    def _parse(self) -> bool:
        """Attempt to parse IPv4 address with optional subnet."""
        pattern = r"""
            (?ix)
            (?P<prefix>.*[^\d])?
            (?P<network>
                (?P<address>\d{1,3}(\.\d{1,3}){3})
                ((?P<subnet>/\d{1,2}))?
            )
            (?P<suffix>[^\d].*)?$
        """.strip()
        matched, result = self._match_regex(pattern)
        if not matched or not is_valid_network(result.get("network")):
            return False
        self._apply_parsed_fields(result)
        return True

    def is_valid_netmask(self) -> bool:
        """Return True if the current value represents a valid IPv4 netmask."""
        full_range = 2 ** 32
        return any((full_range - self.value) == (2 ** bit) for bit in range(32))

    def generate_new(self):
        if not self:
            return self.__class__(self.raw_text)

        if self.is_valid_netmask():
            return self.__class__(self.raw_text)

        new_address = rewritten.new_ipv4_address(self.address)
        return self.__class__(f"{self.prefix}{new_address}{self.subnet}{self.suffix}")


class IPv6Parser(NetworkParser):
    """Parser for IPv6 addresses with utilities for netmask validation and regeneration."""

    def _parse(self) -> bool:
        """Attempt to parse IPv6 address with optional subnet."""
        pattern = r"""
            (?ix)
            (?P<prefix>.*[^0-9a-f:])?
            (?P<network>
                (?P<address>
                    ([0-9a-f]{1,4}(:[0-9a-f]{1,4}){7})|
                    (
                        ([0-9a-f]{1,4}:){0,5}
                        [0-9a-f]{1,4}::[0-9a-f]{1,4}
                        (:[0-9a-f]{1,4}){0,5}
                    )|
                    (:(:[0-9a-f]{1,4}){1,7})|
                    (([0-9a-f]{1,4}:){1,7}:)|
                    (::)
                )
                ((?P<subnet>[/%]\d{1,3}))?
            )
            (?P<suffix>[^0-9a-f:].*)?$
        """.strip()
        matched, result = self._match_regex(pattern)
        if not matched or not is_valid_network(result.get("network")):
            return False
        self._apply_parsed_fields(result)
        return True

    def generate_new(self):
        if not self:
            return self.__class__(self.raw_text)

        new_address = rewritten.new_ipv6_address(self.address)
        return self.__class__(f"{self.prefix}{new_address}{self.subnet}{self.suffix}")


class MACParser:
    """Parse a MAC address and expose its components."""

    def __init__(self, text: str):
        self._text = text
        self._prefix = ""
        self._suffix = ""

        self.info = DotObject(
            address="",
            value=0
        )

        self._parse()

    # ------------------------------------------------------------
    # Magic methods
    # ------------------------------------------------------------

    def __len__(self) -> int:
        """Return 1 if a MAC address was parsed, else 0."""
        return 1 if self.info.address else 0

    def __bool__(self) -> bool:
        """Return True if a MAC address was parsed."""
        return bool(self.info.address)

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
    def address(self) -> str:
        return self.info.address

    @property
    def value(self) -> int:
        return self.info.value

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------

    def _apply_parsed_fields(self, parsed: dict) -> None:
        """Populate info and prefix/suffix from regex results."""
        addr = parsed.get("address", "")
        if addr:
            cleaned = re.sub(r"[.: -]", "", addr)
            self.info.address = addr
            self.info.value = int(cleaned, 16)

        self._prefix = parsed.get("prefix", "") or ""
        self._suffix = parsed.get("suffix", "") or ""

    def _parse(self) -> None:
        """Parse MAC address from raw text."""
        pattern = r"""
            (?ix)
            (?P<prefix>.*[^0-9a-f])?
            (?P<address>
                ([0-9a-f]{2}(:[0-9a-f]{2}){5}) |
                ([0-9a-f]{2}(-[0-9a-f]{2}){5}) |
                ([0-9a-f]{3}([.][0-9a-f]{3}){3}) |
                ([0-9a-f]{12})
            )
            (?P<suffix>[^0-9a-f].*)?$
        """.strip()

        match = re.match(pattern, self._text)
        if not match:
            return

        # Reject pure numeric strings (e.g., "000000000000")
        if re.sub(r"[0-9.]", "", match.group("address")) == "":
            return

        self._apply_parsed_fields(match.groupdict())

    def generate_new(self):
        # Broadcast or zero MAC → return unchanged
        if self:
            if self.value in (0, int("f" * 12, 16)):
                return self.__class__(self.raw_text)

            new_mac_addr = rewritten.new_mac_address(self.address)
            return self.__class__(f"{self.prefix}{new_mac_addr}{self.suffix}")
        return self.__class__(self.raw_text)
