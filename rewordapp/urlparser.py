"""
rewordapp.urlparser
===================

URL parsing and rewriting utilities used to extract components and generate
mapped or obfuscated URL variants.
"""

import re

import rewordapp.rewritten as rewritten
from rewordapp.deps import genericlib_DotObject as DotObject


class URLParser:
    """Parse a MAC address and expose its components."""

    def __init__(self, text: str):
        self._text = text
        self._prefix = ""
        self._suffix = ""

        self.info = DotObject(
            url="",
            scheme="",
            user="",
            host="",
            port="",
            path="",
            query="",
            fragment="",
        )

        self._parse()

    # ------------------------------------------------------------
    # Magic methods
    # ------------------------------------------------------------

    def __len__(self) -> int:
        """Return 1 if URL was parsed, else 0."""
        return 1 if self.info.url else 0

    def __bool__(self) -> bool:
        """Return True if URL was parsed."""
        return bool(self.info.url)

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
    def url(self):
        return self.info.url

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------

    def _apply_parsed_fields(self, parsed: dict) -> None:
        """Populate network_info and prefix/suffix from regex results."""
        self.info.scheme = parsed.get("scheme") or ""
        self.info.user = parsed.get("user") or ""
        self.info.host = parsed.get("host") or ""
        self.info.port = parsed.get("port") or ""
        self.info.path = parsed.get("path") or ""
        self.info.query = parsed.get("query") or ""
        self.info.fragment = parsed.get("fragment") or ""

    def _parse(self) -> None:
        """Parse MAC address from raw text."""
        pattern = r"""(?ix)
            (?P<url>
                (?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*://)?         # scheme
                (?:(?P<user>[^:@]+(?::[^@]+)?@))?               # user
                (?P<host>([a-z][a-z0-9-]+[.])+[a-z][a-z0-9-]+)  # host
                (?::(?P<port>\d+))?                             # port
                (?P<path>/[^\s?#]*)?                            # path
                (?:(?P<query>\?[^\s#]*))?                       # query
                (?:(?P<fragment>\#[^\s]*))?                     # fragment
            )
        """

        match = re.match(pattern, self._text)
        if not match:
            return

        self._prefix = self._text[:match.start()]
        self._suffix = self._text[match.end():]
        self._apply_parsed_fields(match.groupdict())

    def generate_new(self):
        """Generate a rewritten URL using mapped components and return a new parser."""
        scheme = self.info.scheme

        new_user = rewritten.new_url(user=self.info.user)
        new_host = rewritten.new_url(host=self.info.host)
        new_path = rewritten.new_url(path=self.info.path)
        new_query = rewritten.new_url(query=self.info.query)
        new_fragment = rewritten.new_url(fragment=self.info.fragment)

        new_url = (
            f"{self.prefix}"
            f"{scheme}"
            f"{new_user}"
            f"{new_host}"
            f"{new_path}"
            f"{new_query}"
            f"{new_fragment}"
            f"{self.suffix}"
        )

        return URLParser(new_url)
