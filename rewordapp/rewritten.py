"""
rewordapp.rewritten
===================

Utilities for generating randomized character‑substitution maps used for
rewriting or obfuscating text components such as letters, digits, and URL parts.

"""

import string
import random
import re
import ipaddress


def build_char_map(*charsets):
    """Return a randomized one‑to‑one mapping for the given character sets."""
    mapping = {}

    for charset in charsets:
        chars = list(charset)
        shuffled = chars.copy()
        random.shuffle(shuffled)
        mapping.update(zip(chars, shuffled))

    return mapping


def build_ipv4_octet_map() -> dict[str, str]:
    """Build a shuffled mapping for IPv4 octet values from 0–255."""
    mapping = {"0": "0"}  # zero stays fixed

    start = 1
    ranges = [10, 100, 200, 256]

    for stop in ranges:
        original = [str(n) for n in range(start, stop)]
        shuffled = original.copy()
        random.shuffle(shuffled)
        mapping.update(zip(original, shuffled))
        start = stop

    return mapping


class CharMapping:
    """Container for randomized character‑substitution maps used for rewriting text."""

    # Base character groups
    letters_set = (string.ascii_lowercase, string.ascii_uppercase)
    first_digit = random.choice("123456789")

    # General mappings
    letters = build_char_map(*letters_set)
    digits = build_char_map(string.digits)
    base_number = build_char_map(string.digits)
    fraction_number = build_char_map(string.digits)
    alphanumeric = build_char_map(*letters_set, string.digits)

    # URL‑specific mappings
    url_user = build_char_map(*letters_set, string.digits)
    url_host = build_char_map(*letters_set, string.digits)
    url_path = build_char_map(*letters_set, string.digits)
    url_query = build_char_map(*letters_set, string.digits)
    url_fragment = build_char_map(*letters_set, string.digits)

    # MAC address mapping
    mac = (
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
    )

    # IPv4 address mapping
    ipv4 = (
        build_ipv4_octet_map(),
        build_ipv4_octet_map(),
        build_ipv4_octet_map(),
        build_ipv4_octet_map()
    )

    # IPv6 address mapping
    ipv6 = (
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        build_char_map("abcdef", "ABCDEF", "0", "123456789"),
    )

    @classmethod
    def refresh(cls):
        cls.first_digit = random.choice("123456789")

        """Regenerate all character‑mapping tables."""
        cls.letters = build_char_map(*cls.letters_set)
        cls.digits = build_char_map(string.digits)
        cls.base_number = build_char_map(string.digits)
        cls.fraction_number = build_char_map(string.digits)
        cls.alphanumeric = build_char_map(*cls.letters_set, string.digits)

        # URL‑specific mappings
        cls.url_user = build_char_map(*cls.letters_set, string.digits)
        cls.url_host = build_char_map(*cls.letters_set, string.digits)
        cls.url_path = build_char_map(*cls.letters_set, string.digits)
        cls.url_query = build_char_map(*cls.letters_set, string.digits)
        cls.url_fragment = build_char_map(*cls.letters_set, string.digits)

        cls.mac = (
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        )

        cls.ipv4 = (
            build_ipv4_octet_map(),
            build_ipv4_octet_map(),
            build_ipv4_octet_map(),
            build_ipv4_octet_map()
        )

        cls.ipv6 = (
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
            build_char_map("abcdef", "ABCDEF", "0", "123456789"),
        )


def apply_mapping(source: str, mapping: dict) -> str:
    return "".join(mapping.get(ch, ch) for ch in source)

def new_text(
    text: str,
    *,
    letters: bool = False,
    alphanumeric: bool = False,
):
    """Rewrite text using letter or alphanumeric character mappings."""
    if not text.strip():
        return text

    if letters:
        return apply_mapping(text, CharMapping.letters)

    if alphanumeric:
        rewritten = apply_mapping(text, CharMapping.alphanumeric)
        # Prevent leading zero in multi‑character results
        if re.match(r"0[A-Za-z0-9]", rewritten):
            return f"{CharMapping.first_digit}{rewritten[1:]}"
        return rewritten

    return text


def new_url(user="", host="", path="", query="", fragment=""):
    """Rewrite a single URL component using the appropriate character mapping."""

    if user:
        return apply_mapping(user, CharMapping.url_user)
    elif host:
        # Preserve the TLD when rewriting hostnames
        if "." in host:
            domain, tld = host.rsplit(".", maxsplit=1)
            rewritten = apply_mapping(domain, CharMapping.url_host)
            return f"{rewritten}.{tld}"
        return apply_mapping(host, CharMapping.url_host)
    elif path:
        return apply_mapping(path, CharMapping.url_path)
    elif query:
        return apply_mapping(query, CharMapping.url_query)
    elif fragment:
        return apply_mapping(fragment, CharMapping.url_fragment)
    return ""


def new_digits(text: str) -> str:
    """Rewrite a digit‑only string using digit mappings while preserving leading rules."""
    if not text.isdigit():
        return text

    # Zero stays unchanged
    if int(text) == 0:
        return text

    rewritten = apply_mapping(text, CharMapping.digits)

    # Avoid leading zero in multi‑digit results
    if len(rewritten) > 1 and rewritten[0] == "0":
        return f"{CharMapping.first_digit}{rewritten[1:]}"

    return rewritten


def new_number(text: str) -> str:
    """Rewrite a numeric string using number mappings while preserving structure."""
    # Fractional number
    if "." in text:
        try:
            value = float(text)
        except ValueError:
            return text

        if value == 0:
            return text

        base, fraction = text.rsplit(".", maxsplit=1)

        # Preserve literal zeros instead of mapping them
        new_base = base if (base.isdigit() and int(base) == 0) \
            else apply_mapping(base, CharMapping.base_number)

        new_fraction = fraction if (fraction.isdigit() and int(fraction) == 0) \
            else apply_mapping(fraction, CharMapping.fraction_number)

        rewritten = f"{new_base}.{new_fraction}"

        # Avoid leading zero in multi‑digit results
        if re.match(r"0[0-9]", rewritten):
            return f"{CharMapping.first_digit}{rewritten[1:]}"

        return rewritten

    # Integer number
    rewritten = apply_mapping(text, CharMapping.base_number)

    if re.match(r"0[0-9]", rewritten):
        return f"{CharMapping.first_digit}{rewritten[1:]}"

    return rewritten


def new_mac_address(address: str) -> str:
    """Rewrite the second half of a MAC address using mapped octets."""
    stripped = address.strip()

    # Detect separator (., :, space, or -)
    match = re.search(r"[.: -]", stripped)
    sep = match.group() if match else ""

    # Remove all separators
    compact = re.sub(r"[.: -]", "", stripped)

    # Determine octet size: 2 chars normally, 3 chars for dotted format
    octet_size = 3 if sep == "." else 2
    octets = re.findall(f".{{{octet_size}}}", compact)

    count = len(octets)
    if count not in (4, 6):
        return address

    # Rewrite only the second half
    midpoint = count // 2
    rewritten = octets[:midpoint]

    for idx, octet in enumerate(octets[midpoint:]):
        mapped = apply_mapping(octet, CharMapping.mac[idx])
        rewritten.append(mapped)

    return sep.join(rewritten)


def new_ipv4_address(address: str) -> str:
    """Rewrite an IPv4 address by remapping octets 2–4 using predefined mappings."""
    octets = address.strip().split(".")
    if len(octets) != 4:
        return address

    new_octets = []
    for idx, octet in enumerate(octets):
        new_octet = octet if idx == 0 else CharMapping.ipv4[idx].get(octet, octet)
        new_octets.append(new_octet)
    return ".".join(new_octets)


def new_ipv6_address(address: str) -> str:
    """Rewrite an IPv6 address by remapping groups after the first non‑zero group."""
    stripped = address.strip()

    # Preserve original casing style (uppercase hex vs lowercase)
    is_uppercase = re.sub(r"[0-9:]+", "", stripped).isupper()

    # Normalize to full 8‑group exploded form
    full = ipaddress.ip_address(stripped).exploded

    # Unspecified address stays unchanged
    if full == "0000:" * 7 + "0000":
        return address

    groups = full.split(":")
    rewritten = []
    rewrite_started = False

    for index, group in enumerate(groups):
        if rewrite_started:
            mapped = apply_mapping(group, CharMapping.ipv6[index])
            rewritten.append(mapped)
        else:
            rewritten.append(group)
            # Begin rewriting after the first non‑zero group
            if group.strip("0"):
                rewrite_started = True

    compressed = ipaddress.ip_address(":".join(rewritten)).compressed
    return compressed.upper() if is_uppercase else compressed
