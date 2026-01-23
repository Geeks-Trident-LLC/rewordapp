import re
import ipaddress
from rewordapp.deps import genericlib_DotObject as DotObject


def is_valid_network(network: str) -> bool:
    """
    Validate whether a string is a valid IPv4 or IPv6 network address,
    including optional subnet length.
    """
    try:
        # Split into base address and optional subnet
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
        self.network_info = DotObject(
            network="",
            address="",
            full_address="",
            subnet="",
            version=0
        )
        self._prefix = ""
        self._suffix = ""
        self._parse_network()

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
    def version(self) -> int:
        return self.network_info.version

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
