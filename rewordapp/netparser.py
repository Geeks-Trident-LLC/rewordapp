import re
import ipaddress
from rewordapp.deps import genericlib_DotObject as DotObject


def is_valid_network(network: str) -> bool:
    try:
        address, *remainder = re.split(r"[%/]", network, maxsplit=2)
        subnet = remainder[0] if remainder else None
        net = ipaddress.ip_network(address)

        if subnet is None:
            return True

        if net.version == 4:
            subnet = int(subnet) if subnet.isdigit() else 0
            return 1 <= subnet <= 32

        subnet = int(subnet) if subnet.isdigit() else 0
        return 1 <= subnet <= 128
    except Exception:   # noqa
        return False


class NetworkParser:
    """
    Parse and store IPv4/IPv6 network information from raw input text.
    """

    def __init__(self, raw_text: str):
        self._raw_text = raw_text
        self.network_info = DotObject(
            network="",
            address="",
            subnet="",
        )
        self._prefix = ""
        self._suffix = ""
        self._parse()

    def __len__(self) -> int:
        return 1 if self.network_info.network else 0

    def __bool__(self) -> bool:
        return bool(self.network_info.network)

    @property
    def raw_text(self) -> str:
        return self._raw_text

    @property
    def prefix(self) -> str:
        return self._prefix or ""

    @property
    def suffix(self) -> str:
        return self._suffix or ""

    @property
    def network(self) ->str:
        return self.network_info.network or ""

    @property
    def address(self) ->str:
        return self.network_info.address or ""

    @property
    def subnet(self) ->str:
        return self.network_info.subnet or ""


    def _match_pattern(self, pattern: str) -> tuple[bool, dict]:
        match = re.match(pattern, self.raw_text)
        return (True, match.groupdict()) if match else (False, {})

    def _update_network_info(self, parsed: dict) -> None:
        self.network_info.network = parsed.get("network", "")
        self.network_info.address = parsed.get("address", "")
        self.network_info.subnet = parsed.get("subnet", "")
        self._prefix = parsed.get("prefix", "")
        self._suffix = parsed.get("suffix", "")

    def _parse_ipv6(self) -> bool:
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
        matched, result = self._match_pattern(pattern)
        if not matched:
            return False

        valid = is_valid_network(result.get("network"))
        if not valid:
            return False

        self._update_network_info(result)
        return True

    def _parse_ipv4(self) -> bool:
        pattern = r"""
            (?ix)
            (?P<prefix>.*[^\d])?                          
            (?P<network>                                    
                (?P<address>\d{1,3}(\.\d{1,3}){3})      
                (/(?P<subnet>\d{1,2}))?                      
            )
            (?P<suffix>[^\d].*)?$                        
        """.strip()
        matched, result = self._match_pattern(pattern)
        if not matched:
            return False

        valid = is_valid_network(result.get("network"))
        if not valid:
            return False

        self._update_network_info(result)
        return True

    def _parse(self) -> None:
        """Attempt to parse the raw text as IPv6, then IPv4."""
        if not self._parse_ipv6():
            self._parse_ipv4()
