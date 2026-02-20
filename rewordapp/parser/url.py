"""
rewordapp.parser.url
====================

URL parsing and rewriting utilities used to extract components and generate
mapped or obfuscated URL variants.
"""

import re

import rewordapp.rewrite.rewritten as rewritten
from rewordapp.deps import genericlib_DotObject as DotObject
from rewordapp import PATTERN

import rewordapp.rewrite.checker as checker


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
    def raw(self) -> str:
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
        self._prefix = parsed.get("prefix") or ""
        self._suffix = parsed.get("suffix") or ""
        self.info.scheme = parsed.get("scheme") or ""
        self.info.user = parsed.get("user") or ""
        self.info.host = parsed.get("host") or ""
        self.info.port = parsed.get("port") or ""
        self.info.path = parsed.get("path") or ""
        self.info.query = parsed.get("query") or ""
        self.info.fragment = parsed.get("fragment") or ""
        self.info.url = "".join(
            [
                self.info.scheme, self.info.user, self.info.host,
                self.info.port, self.info.path, self.info.query,
                self.info.fragment
            ]
        )

    def _parse(self) -> None:
        """Parse MAC address from raw text."""

        pattern = rf"""(?ix)
            (?P<prefix>{PATTERN.punct}*)
            (?P<url>
                (?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*://)?         # scheme
                (?:(?P<user>[^:@]+(?::[^@]+)?@))?               # user
                (?P<host>([a-z][a-z0-9-]+[.])+[a-z][a-z0-9-]+)  # host
                (?::(?P<port>\d+))?                             # port
                (?P<path>/[a-z0-9_./]+)?                        # path
                (?:(?P<query>\?[a-z0-9_.=&]+))?                 # query
                (?:(?P<fragment>\#[a-z0-9_.%]+))?               # fragment
            )
            (?P<suffix>{PATTERN.punct}*)
        """

        match = re.fullmatch(pattern, self._text)
        if not match:
            return

        host = match.group("host")

        # Validate TLD
        if not checker.has_common_tld(host):
            return

        # # Validate subdomain (if present)
        # if host.count(".") > 1 and not checker.has_common_subdomain(host):
        #     return

        # Extract prefix/suffix around the matched URL
        # self._prefix = self._text[: match.start()] or ""
        # self._suffix = self._text[match.end():] or ""

        # Apply parsed fields to internal state
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
