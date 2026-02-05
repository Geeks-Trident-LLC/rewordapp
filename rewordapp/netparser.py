import random
from typing import List, Sequence

import re
import ipaddress
from copy import deepcopy

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


def pick_new_octet_value(octet) -> str:
    """Return a new octet value different from the original."""
    value = octet.value
    net_type = octet.net_type

    # Zero-handling
    if value == 0:
        if net_type == "mac":
            return "00" if octet.width == 2 else "000"
        return "0"

    # Range boundaries by net_type
    if net_type == "ipv4":
        boundaries: Sequence[int] = (10, 100, 256)
    elif net_type == "ipv6":
        boundaries = (16, 256, 4096, 65536)
    else:  # MAC or other hex-based
        boundaries = (16, 256, 4096)

    start = 0
    for stop in boundaries:
        if start <= value < stop:
            candidates = list(range(start, stop))
            candidates.remove(value)
            new_value = random.choice(candidates)

            if net_type == "mac":
                return format(new_value, "02x" if octet.width == 2 else "03x")
            if net_type == "ipv4":
                return str(new_value)
            return format(new_value, "x")

        start = stop

    # Fallback
    if net_type in ("ipv4", "ipv6"):
        return "0"
    return "00" if octet.width == 2 else "000"


class Octet:
    """
    Represents a single IPv4 or IPv6 octet/segment and provides utilities
    for generating alternate values.
    """

    def __init__(self, data: str = "", position: int = 0, net_type: str = ""):
        """
        Parameters
        ----------
        data : str
            The octet value in string form (decimal for IPv4, hex for IPv6).
        position : int
            Index of this octet within the full address.
        net_type : str or optional
            ipv4, ipv6, or MAC.
        """
        self.net_type = net_type
        self.data = str(data)
        self.width = len(self.data)
        self.position = position

        base = 10 if net_type == "ipv4" else 16
        self.value = int(self.data, base=base) if self.data else 0

    @property
    def hex_value(self):
        if self.net_type == "mac":
            return format(self.value, "02x" if self.width == 2 else "03x")
        return format(self.value, "02x" if self.net_type == "ipv4" else "04x")

    def __len__(self) -> int:
        """Return 1 if the octet contains data, otherwise 0."""
        return 1 if self.data else 0

    def __bool__(self) -> bool:
        """Return True if the octet contains data."""
        return bool(self.data)

    def __eq__(self, other):
        """Return True if both octets have the same value."""
        return self.value == other.value

    def __ne__(self, other):
        """Return True if the octets differ in value."""
        return self.value != other.value

    def clone(self):
        """Return a deep copy of this Octet."""
        return deepcopy(self)

    def generate_new(self) -> "Octet":
        """
        Create a new Octet instance with a different value
        using the alternate-octet generator.
        """
        new_data = pick_new_octet_value(self)
        return Octet(data=new_data, position=self.position, net_type=self.net_type)


class Octets:
    """
    Container for IPv4 or IPv6 octets/segments with utilities
    for cloning and generating alternate addresses.
    """

    def __init__(self, address: str = "", net_type=""):
        """
        Initialize and parse an IPv4/IPv6 address into Octet objects.
        """
        self.address = address.strip()
        self.net_type = net_type
        self.octets: List[Octet] = []
        self._parse_address()

    def __len__(self) -> int:
        """Return the number of octets."""
        return len(self.octets)

    def __bool__(self) -> bool:
        """Return True if octets were parsed."""
        return bool(self.octets)

    @property
    def is_ipv4(self) -> bool:
        """Return True if the address is IPv4."""
        return self.net_type == "ipv4"

    @property
    def is_ipv6(self) -> bool:
        """Return True if the address is IPv6."""
        return self.net_type == "ipv6"

    @property
    def is_mac(self):
        """Return True if the address is MAC."""
        return self.net_type == "mac"

    def _parse_address(self) -> None:
        """Split the address and build Octet objects."""
        parts = re.findall(r"\w\w", self.address)
        if re.search(r"[.:-]", self.address):
            parts = re.split(r"[.:-]", self.address)

        for position, value in enumerate(parts):
            self.octets.append(
                Octet(data=value, position=position, net_type=self.net_type)
            )

    def contains_octet(self, octet):
        """Return True if an octet at the same position matches."""
        return self.get_octet(octet.position) == octet

    def sync_by_position(self, octets, position):
        """Replace the octet at the given position with a clone."""
        self.octets[position] = octets.get_octet(position).clone()

    def get_octet(self, index: int = 0) -> Octet:
        """Return the octet at the given index, or an empty Octet if invalid."""
        if not self or not isinstance(index, int):
            return Octet()

        try:
            return self.octets[index]
        except IndexError:
            return Octet()

    def first_nonzero_octet(self) -> Octet:
        """Return the first octet whose value is greater than zero."""
        for octet in self.octets:
            if octet.value > 0:
                return octet
        return self.get_octet(0)

    def total_nonzero_octet(self) -> int:
        """Return the total number of octets whose value is greater than zero."""
        total = 0
        for octet in self.octets:
            if octet.value > 0:
                total += 1
        return total

    def generate_new(self) -> "Octets":
        """Generate a new octets"""

        if self.net_type == "mac":
            half = 2 if len(self) == 4 else 3
            new_octets = [o.clone() for o in self.octets[:half]] + [
                o.generate_new() for o in self.octets[half:]]
        else:
            if self.total_nonzero_octet() <= 1:
                # new_octets = [o.generate_new() if o.value > 0 else o.clone() for o in self.octets]
                new_octets = [o.generate_new() for o in self.octets]
            else:
                first_nonzero = self.first_nonzero_octet()
                pivot = first_nonzero.position + 1 if self.is_ipv6 else 1
                new_octets = [o.clone() for o in self.octets[:pivot]]

                for index in range(pivot, len(self.octets)):
                    new_octets.append(self.get_octet(index).generate_new())

        if self.net_type == "ipv4":
            new_address = ".".join(str(o.value) for o in new_octets)
            return self.__class__(address=new_address, net_type=self.net_type)
        elif self.net_type == "ipv6":
            new_address = ":".join(o.hex_value for o in new_octets)
            return self.__class__(address=new_address, net_type=self.net_type)
        else:
            match = re.search("[:.-]", self.address)
            joiner = match.group() if match else ""
            new_address = joiner.join(o.hex_value for o in new_octets)
            return self.__class__(address=new_address, net_type=self.net_type)

    def to_address(self) -> str:
        """Return the address as a string."""
        if self.net_type in ("ipv4", "ipv6"):
            joiner = "." if self.is_ipv4 else ":"
            address = joiner.join(o.data for o in self.octets)
            return ipaddress.ip_address(address).compressed
        return self.address

    def to_full_address(self) -> str:
        """Return the full address as a string."""
        if self.net_type in ("ipv4", "ipv6"):
            joiner = "." if self.is_ipv4 else ":"
            address = joiner.join(o.data for o in self.octets)
            return ipaddress.ip_address(address).exploded
        return self.address


class NetworkParser:
    """
    Extract and store IPv4/IPv6 network details from raw input text.
    """

    def __init__(self, text: str):
        self._text = text
        self.info = DotObject(
            network="",
            address="",
            full_address="",
            subnet="",
            version=0,
            value=0,
            octets=Octets(address=""),
        )
        self._prefix = ""
        self._suffix = ""
        self._parse_network()
        self.new_parser = None

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
    def full_address(self) -> str:
        return self.info.full_address or ""

    @property
    def subnet(self) -> str:
        return self.info.subnet or ""

    @property
    def subnet_joiner(self) -> str:
        if self.subnet:
            return "%" if "%" in self.network else "/"
        return ""

    @property
    def version(self) -> int:
        return self.info.version

    @property
    def value(self):
        return self.info.value or 0

    @property
    def octets(self) -> Octets:
        return self.info.octets

    # --- Internal helpers ---
    def _match_regex(self, pattern: str) -> tuple[bool, dict]:
        """Try matching the raw text against a regex pattern."""
        match = re.match(pattern, self._text)
        return (True, match.groupdict()) if match else (False, {})

    def _apply_parsed_fields(self, parsed: dict) -> None:
        """Update info fields from regex results."""
        self.info.network = parsed.get("network", "")
        self.info.address = parsed.get("address", "")
        if self.info.address:
            addr = ipaddress.ip_address(self.info.address)
            self.info.update(full_address=addr.exploded)
            self.info.update(version=addr.version)
            self.info.update(value=int(addr))
            self.info.update(
                octets=Octets(
                    address=addr.exploded,
                    net_type="ipv4" if addr.version == 4 else "ipv6"
                )
            )
        self.info.subnet = parsed.get("subnet", "")
        self._prefix = parsed.get("prefix", "")
        self._suffix = parsed.get("suffix", "")

    def _parse_ipv6(self) -> bool:
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
                ([/%](?P<subnet>\d{1,3}))?
            )
            (?P<suffix>[^0-9a-f:].*)?$
        """.strip()
        matched, result = self._match_regex(pattern)
        if not matched or not is_valid_network(result.get("network")):
            return False
        self._apply_parsed_fields(result)
        return True

    def _parse_ipv4(self) -> bool:
        """Attempt to parse IPv4 address with optional subnet."""
        pattern = r"""
            (?ix)
            (?P<prefix>.*[^\d])?
            (?P<network>
                (?P<address>\d{1,3}(\.\d{1,3}){3})
                (/(?P<subnet>\d{1,2}))?
            )
            (?P<suffix>[^\d].*)?$
        """.strip()
        matched, result = self._match_regex(pattern)
        if not matched or not is_valid_network(result.get("network")):
            return False
        self._apply_parsed_fields(result)
        return True

    def _parse_network(self) -> None:
        """Try parsing as IPv6 first, then IPv4."""
        if not self._parse_ipv6():
            self._parse_ipv4()

    def sync_octets(self, other):
        if type(self) == type(other) and len(self.octets) == len(other.octets):
            octets = self.info.octets.octets
            for index, octet in enumerate(octets):
                other_octet = other.octets.get_octet(index)
                if octet != other_octet:
                    octets[index] = other_octet.clone()


class IPv4Parser(NetworkParser):
    """Parser for IPv4 addresses with utilities for netmask validation and regeneration."""

    def is_valid_netmask(self) -> bool:
        """Return True if the current value represents a valid IPv4 netmask."""
        full_range = 2 ** 32
        return any((full_range - self.value) == (2 ** bit) for bit in range(32))

    def generate_new(self, source_parsers=None):
        """
        Generate a new IPv4Parser instance based on alternate octet generation
        and optional reference patterns from other IPv4Parser objects.
        """
        source_parsers = source_parsers if isinstance(source_parsers, (list, tuple)) else []

        # Netmask values remain unchanged
        if self.is_valid_netmask():
            self.new_parser = IPv4Parser(self.address)
            return self.new_parser

        # Build new base address
        new_base = self.octets.generate_new().to_address()
        combined = (
            f"{new_base}{self.subnet_joiner}{self.subnet}"
            if self.subnet
            else new_base
        )

        self.new_parser = IPv4Parser(combined)

        # Filter only IPv4 sources
        ipv4_sources = [src for src in source_parsers if src.version == 4]
        if not ipv4_sources:
            return self.new_parser

        # If an identical source exists, sync directly
        identical = [src for src in ipv4_sources if src.value == self.value]
        if identical:
            self.new_parser.sync_octets(identical[0].new_parser)
            return self.new_parser

        # Otherwise sync individual octets when matching patterns exist
        for index in range(1, 4):
            current_octet = self.octets.get_octet(index)
            matching_sources = [
                src for src in ipv4_sources
                if src.octets.contains_octet(current_octet)
            ]
            if matching_sources:
                self.new_parser.octets.sync_by_position(
                    matching_sources[0].new_parser.octets,
                    current_octet.position
                )

        return self.new_parser


class IPv6Parser(NetworkParser):
    """Parser for IPv6 addresses with utilities for netmask validation and regeneration."""

    def generate_new(self, source_parsers=None):
        """
        Generate a new IPv6Parser instance based on alternate octet generation
        and optional reference patterns from other IPv6Parser objects.
        """
        source_parsers = source_parsers if isinstance(source_parsers, (list, tuple)) else []

        # Build new base address
        new_base = self.octets.generate_new().to_address()
        combined = (
            f"{new_base}{self.subnet_joiner}{self.subnet}"
            if self.subnet
            else new_base
        )

        self.new_parser = IPv6Parser(combined)

        # Filter only IPv6 sources
        ipv6_sources = [src for src in source_parsers if src.version == 6]
        if not ipv6_sources:
            return self.new_parser

        # If an identical source exists, sync directly
        identical = [src for src in ipv6_sources if src.value == self.value]
        if identical:
            self.new_parser.sync_octets(identical[0].new_parser)
            return self.new_parser

        first_nonzero = self.octets.first_nonzero_octet()
        pivot = first_nonzero.position + 1

        for index in range(pivot, 8):
            current_octet = self.octets.get_octet(index)
            matching_sources = [
                src for src in ipv6_sources
                if src.octets.contains_octet(current_octet)
            ]
            if matching_sources:
                self.new_parser.octets.sync_by_position(
                    matching_sources[0].new_parser.octets,
                    current_octet.position
                )

        return self.new_parser


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

        self._parse_mac()

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

    def _parse_mac(self) -> None:
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
