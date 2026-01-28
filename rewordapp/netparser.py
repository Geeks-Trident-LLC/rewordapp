import random
from typing import List, Sequence

import re
import ipaddress
from copy import deepcopy

from rewordapp.deps import genericlib_DotObject as DotObject


def is_valid_network(network: str) -> bool:
    """
    Validate whether a string is a valid IPv4 or IPv6 network address,
    including optional subnet length.
    """
    try:
        # Split into ip_type address and optional subnet
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


def generate_alternate_octet(octet) -> str:
    """
    Generate a new octet value different from the original, based on IPv4 or IPv6 rules.

    Parameters
    ----------
    octet : "Octet"
        An object with attributes:
        - value (int): The current octet value.
        - ip_type (int): Either 4 (IPv4) or 6 (IPv6).

    Returns
    -------
    str
        A new octet value as a string. For IPv4, the value is returned in decimal.
        For IPv6, the value is returned in hexadecimal (without the '0x' prefix).

    Notes
    -----
    - For IPv6, if the value is 0, the function returns "0".
    - IPv4 ranges are segmented into: [0–9], [10–99], [100–255].
    - IPv6 ranges are segmented into 4-bit blocks: 0–15, 16–255, 256–4095, 4096–65535.
    """
    original_value = octet.value
    ip_type = octet.ip_type

    if original_value == 0:
        return "0"

    # Define range boundaries
    if ip_type == 4:
        boundaries: Sequence[int] = (10, 100, 256)
    else:
        boundaries = (16, 256, 4096, 65536)

    start = 0
    for stop in boundaries:
        if start <= original_value < stop:
            # Build candidate pool excluding the original value
            candidates = list(range(start, stop))
            candidates.remove(original_value)

            # Choose a new value
            new_value = random.choice(candidates)

            # Format output
            return str(new_value) if ip_type == 4 else format(new_value, "x")

        start = stop

    # Fallback (should rarely occur)
    return "0"



class Octet:
    """
    Represents a single IPv4 or IPv6 octet/segment and provides utilities
    for generating alternate values.
    """

    def __init__(self, data: str = "", position: int = 0, ip_type: int = 4):
        """
        Parameters
        ----------
        data : str
            The octet value in string form (decimal for IPv4, hex for IPv6).
        position : int
            Index of this octet within the full address.
        ip_type : int
            Either 4 (IPv4) or 6 (IPv6).
        """
        self.ip_type = ip_type
        self.data = str(data)
        self.position = position

        base = 10 if ip_type == 4 else 16
        self.value = int(self.data, base=base) if self.data else 0

    @property
    def hex_value(self):
        return format(self.value, "02x" if self.ip_type == 4 else "04x")

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
        new_data = generate_alternate_octet(self)
        return Octet(data=new_data, position=self.position, ip_type=self.ip_type)


class Octets:
    """
    Container for IPv4 or IPv6 octets/segments with utilities
    for cloning and generating alternate addresses.
    """

    def __init__(self, address: str = ""):
        """
        Initialize and parse an IPv4/IPv6 address into Octet objects.
        """
        self.address = address.strip()
        self.ip_type = 4
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
        return self.ip_type == 4

    @property
    def is_ipv6(self) -> bool:
        """Return True if the address is IPv6."""
        return self.ip_type == 6

    def _parse_address(self) -> None:
        """Split the address and build Octet objects."""
        parts = re.split(r"[.:]", self.address)
        self.ip_type = 4 if len(parts) == 4 else 6

        for position, value in enumerate(parts):
            self.octets.append(
                Octet(data=value, position=position, ip_type=self.ip_type)
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

    def generate_new(self) -> "Octets":
        """Generate a new octets"""
        first_nonzero = self.first_nonzero_octet()
        pivot = first_nonzero.position + 1 if self.is_ipv6 else 1
        new_octets = [o.clone() for o in self.octets[:pivot]]

        for index in range(pivot, len(self.octets)):
            new_octets.append(self.get_octet(index).generate_new())

        if self.ip_type == 4:
            new_address = ".".join(str(o.value) for o in new_octets)
            return self.__class__(address=new_address)

        new_address = ":".join(o.hex_value for o in new_octets)
        return self.__class__(address=new_address)

    def to_address(self) -> str:
        """Return the address as a string."""
        joiner = "." if self.is_ipv4 else ":"
        return joiner.join(o.data for o in self.octets)


class NetworkParser:
    """
    Extract and store IPv4/IPv6 network details from raw input text.
    """

    def __init__(self, text: str):
        self._text = text
        self.network_info = DotObject(
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
        return 1 if self.network_info.network else 0

    def __bool__(self) -> bool:
        """Return True if a network was parsed, else False."""
        return bool(self.network_info.network)

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
        return self.network_info.network or ""

    @property
    def address(self) -> str:
        return self.network_info.address or ""

    @property
    def full_address(self) -> str:
        return self.network_info.full_address or ""

    @property
    def subnet(self) -> str:
        return self.network_info.subnet or ""

    @property
    def subnet_joiner(self) -> str:
        if self.subnet:
            return "%" if "%" in self.network else "/"
        return ""

    @property
    def version(self) -> int:
        return self.network_info.version

    @property
    def value(self):
        return self.network_info.value or 0

    @property
    def octets(self) -> Octets:
        return self.network_info.octets

    # --- Internal helpers ---
    def _match_regex(self, pattern: str) -> tuple[bool, dict]:
        """Try matching the raw text against a regex pattern."""
        match = re.match(pattern, self._text)
        return (True, match.groupdict()) if match else (False, {})

    def _set_network_info(self, parsed: dict) -> None:
        """Update network_info fields from regex results."""
        self.network_info.network = parsed.get("network", "")
        self.network_info.address = parsed.get("address", "")
        if self.network_info.address:
            addr = ipaddress.ip_address(self.network_info.address)
            self.network_info.update(full_address=addr.exploded)
            self.network_info.update(version=addr.version)
            self.network_info.update(value=int(addr))
            self.network_info.update(octets=Octets(address=addr.exploded))
        self.network_info.subnet = parsed.get("subnet", "")
        self._prefix = parsed.get("prefix", "")
        self._suffix = parsed.get("suffix", "")

    def _parse_ipv6(self) -> bool:
        """Attempt to parse IPv6 address with optional subnet."""
        pattern = r"""
            (?ix)
            (?P<prefix>.*[^0-9a-f])?
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
            (?P<suffix>[^0-9a-f].*)?$
        """.strip()
        matched, result = self._match_regex(pattern)
        if not matched or not is_valid_network(result.get("network")):
            return False
        self._set_network_info(result)
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
        self._set_network_info(result)
        return True

    def _parse_network(self) -> None:
        """Try parsing as IPv6 first, then IPv4."""
        if not self._parse_ipv6():
            self._parse_ipv4()

    def sync_octets(self, other):
        if type(self) == type(other):
            for index, octet in enumerate(self.network_info.octets):
                other_octet = other.octets.get_octet(index)
                if octet != other_octet:
                    self.network_info.octets[index] = other_octet.clone()


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
