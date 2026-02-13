"""
rewordapp.rewritten
===================

Utilities for generating randomized character‑substitution maps used for
rewriting or obfuscating text components such as letters, digits, and URL parts.

"""

import string
from string import ascii_lowercase
from string import ascii_uppercase
from string import digits
import random
import re
import ipaddress


def refresh() -> None:
    """Refresh all character‑mapping tables."""
    CharMapping.refresh()


def shuffle_until_unique(origin, attempts=10):
    """Shuffle a list until no element remains in its original position."""
    shuffled = origin.copy()

    for _ in range(attempts):
        random.shuffle(shuffled)

        # A position is allowed to match only if the value is zero-like ("0", "00", etc.)
        if all(
            str(item).strip("0") == "" or str(item) != str(origin[i])
            for i, item in enumerate(shuffled)
        ):
            return shuffled

    # Fallback: return a final shuffle even if a full derangement wasn't achieved
    random.shuffle(shuffled)
    return shuffled


def build_char_map(*charsets):
    """Return a randomized one‑to‑one mapping for the given character sets."""
    mapping = {}

    for charset in charsets:
        chars = list(charset)
        mapping.update(zip(chars, shuffle_until_unique(chars)))

    return mapping


def build_ipv4_octet_map() -> dict[str, str]:
    """Build a shuffled mapping for IPv4 octet values from 0–255."""
    mapping = {"0": "0"}  # zero stays fixed

    start = 1
    ranges = [10, 100, 200, 256]

    for stop in ranges:
        original = [str(n) for n in range(start, stop)]
        mapping.update(zip(original, shuffle_until_unique(original)))
        start = stop

    return mapping


def generate_random_binary(source):
    """Return a zero‑padded binary string with the same length as the source."""
    width = len(source)
    value = random.randrange(2 ** width)
    return format(value, f"0{width}b")



class CharMapping:
    """Container for randomized character‑substitution maps used for rewriting text."""

    # Base character groups
    letters_set = (ascii_lowercase, ascii_uppercase)
    first_digit = random.choice(digits[1:])
    digits_set = (digits[:1], digits[1:])
    hex_set = (ascii_lowercase[:6], ascii_uppercase[:6], *digits_set)
    alphanumeric_set = (*hex_set, ascii_lowercase[6:], ascii_uppercase[6:])

    # General mappings
    letters = build_char_map(*letters_set)
    base_number = build_char_map(*digits_set)
    fraction_number = build_char_map(*digits_set)
    alphanumeric = build_char_map(*alphanumeric_set)
    octal = build_char_map(digits[:1], digits[1:-2])
    file_permission = build_char_map(digits[:8])
    win_file_mode = build_char_map("-", "d", "D", "ahilrs", "AHILRS")

    # URL‑specific mappings
    url_user = build_char_map(*alphanumeric_set)
    url_host = build_char_map(*alphanumeric_set)
    url_path = build_char_map(*alphanumeric_set)
    url_query = build_char_map(*alphanumeric_set)
    url_fragment = build_char_map(*alphanumeric_set)

    # MAC address mapping
    mac = (
        build_char_map(*hex_set),
        build_char_map(*hex_set),
        build_char_map(*hex_set),
        build_char_map(*hex_set),
        build_char_map(*hex_set),
        build_char_map(*hex_set),
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
        build_char_map(*hex_set),
        build_char_map(*hex_set),
        build_char_map(*hex_set),
        build_char_map(*hex_set),
        build_char_map(*hex_set),
        build_char_map(*hex_set),
        build_char_map(*hex_set),
        build_char_map(*hex_set)
    )

    @classmethod
    def refresh(cls):
        """Regenerate all character‑mapping tables."""

        cls.first_digit = random.choice("123456789")
        # General mappings
        cls.letters = build_char_map(*cls.letters_set)
        cls.base_number = build_char_map(*cls.digits_set)
        cls.fraction_number = build_char_map(*cls.digits_set)
        cls.alphanumeric = build_char_map(*cls.alphanumeric_set)
        cls.octal = build_char_map(digits[:1], digits[1:-2])
        cls.file_permission = build_char_map(digits[:8])
        win_file_mode = build_char_map("-", "d", "D", "ahilrs", "AHILRS")

        # URL‑specific mappings
        cls.url_user = build_char_map(*cls.alphanumeric_set)
        cls.url_host = build_char_map(*cls.alphanumeric_set)
        cls.url_path = build_char_map(*cls.alphanumeric_set)
        cls.url_query = build_char_map(*cls.alphanumeric_set)
        cls.url_fragment = build_char_map(*cls.alphanumeric_set)

        # MAC address mapping
        cls.mac = (
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set)
        )

        # IPv4 address mapping
        cls.ipv4 = (
            build_ipv4_octet_map(),
            build_ipv4_octet_map(),
            build_ipv4_octet_map(),
            build_ipv4_octet_map()
        )

        # IPv6 address mapping
        cls.ipv6 = (
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set),
            build_char_map(*cls.hex_set)
        )


def apply_mapping(text: str, mapping: dict[str, str]) -> str:
    """Rewrite a string by applying character mappings, with special handling for hex, binary, and octal prefixes."""
    # Hexadecimal: 0xNN...
    if re.fullmatch(r"(?i)0x[a-f0-9]+", text):
        return text[:2] + "".join(mapping.get(ch, ch) for ch in text[2:])

    # Binary: 0bNN...
    if re.fullmatch(r"(?i)0b[01]+", text):
        return text[:2] + generate_random_binary(text[2:])

    # Octal: 0oNN... or 0NN...
    if re.fullmatch(r"(?i)0o?[0-7]+", text):
        prefix_len = 2 if "o" in text.lower() else 1
        return text[:prefix_len] + "".join(
            CharMapping.octal.get(ch, ch) for ch in text[prefix_len:]
        )

    # Default: apply generic mapping
    return "".join(mapping.get(ch, ch) for ch in text)


def new_word(text: str) -> str:
    """Rewrite a word while preserving punctuation and applying the appropriate character mapping."""
    if not text.strip():
        return text

    # Choose mapping based on whether the segment is pure letters
    def select_mapping(segment: str):
        if re.fullmatch(r"[A-Za-z]", segment):
            return CharMapping.letters
        return CharMapping.alphanumeric

    punct_pattern = f"[{re.escape(string.punctuation)}]+"

    # If punctuation appears, rewrite only the non‑punctuation segments
    if re.search(punct_pattern, text):
        parts = []
        start = 0
        match = None

        for match in re.finditer(punct_pattern, text):
            before = text[start:match.start()]
            parts.append(apply_mapping(before, select_mapping(before)))
            parts.append(match.group())     # keep punctuation unchanged
            start = match.end()

        if match:
            after = text[match.end():]
            parts.append(apply_mapping(after, select_mapping(after)))

        return "".join(parts)

    # No punctuation → rewrite whole word
    return apply_mapping(text, select_mapping(text))


def new_url(user="", host="", path="", query="", fragment=""):
    """Rewrite a single URL component using the appropriate character mapping."""
    # User component
    if user:
        return apply_mapping(user, CharMapping.url_user)

    # Host component (preserve TLD)
    if host:
        if host.count(".") == 0:
            return apply_mapping(host, CharMapping.url_host)

        if host.count(".") == 1:
            domain, tld = host.rsplit(".", maxsplit=1)
            rewritten = apply_mapping(domain, CharMapping.url_host)
            return f"{rewritten}.{tld}"
        subdomain, *other, tld = host.split(".")
        rewritten = apply_mapping(".".join(other), CharMapping.url_host)
        if re.fullmatch(r"(?i)[a-z][a-z0-9]+", subdomain):
            return f"{subdomain}.{rewritten}.{tld}"

        rewritten_subdomain = apply_mapping(subdomain, CharMapping.url_host)
        return f"{rewritten_subdomain}.{rewritten}.{tld}"


    # Determine which component is present
    if path:
        data, mapping = path, CharMapping.url_path
    elif query:
        data, mapping = query, CharMapping.url_query
    elif fragment:
        data, mapping = fragment, CharMapping.url_fragment
    else:
        return ""

    # Preserve percent‑encoded sequences
    encoded_re = r"(?i)%[a-f0-9]{2}"
    if re.search(encoded_re, data):
        parts = []
        start = 0
        last_match = None

        for match in re.finditer(encoded_re, data):
            before = data[start:match.start()]
            parts.append(apply_mapping(before, mapping))
            parts.append(match.group())  # keep %XX unchanged
            start = match.end()
            last_match = match

        if last_match:
            after = data[last_match.end():]
            parts.append(apply_mapping(after, mapping))

        return "".join(parts)

    # No percent‑encoding → rewrite whole component
    return apply_mapping(data, mapping)


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

    # binary
    if re.fullmatch("0[01]+", text):
        return generate_random_binary(text)

    # octal
    if re.fullmatch("0[0-7]+", text):
        return apply_mapping(text, CharMapping.octal)

    # generic integer
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
    if count % 2 == 1 or count % 2 == 0 and count < 4:
        return address

    # Rewrite only the second half
    midpoint = count // 2 if count in (4, 6) else 3
    rewritten = octets[:midpoint]

    for idx, octet in enumerate(octets[midpoint:]):
        mapped = apply_mapping(octet, CharMapping.mac[idx % 6])
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


def new_fperm(perm: str) -> str:
    """Rewrite owner/group/other permission bits using mapped patterns."""
    def remap(bits: str) -> str:
        original = bits
        value = int("".join("0" if c == "-" else "1" for c in bits), 2)
        new_value = int(CharMapping.file_permission.get(str(value), str(value)))

        mapping = "rwx"
        parts = [
            "-" if b == "0" else mapping[i]
            for i, b in enumerate(format(new_value, "03b"))
        ]

        # Preserve special characters (s, S, t, T, etc.)
        for i, ch in enumerate(original):
            if ch not in "rwx-":
                parts[i] = ch

        return "".join(parts)

    if len(perm) >= 10:
        # Skip rewriting if no permission bits are set
        if perm[1:10] == "-" * 9:
            return perm

        file_type = perm[0]
        owner = remap(perm[1:4])
        group = remap(perm[4:7])
        other = remap(perm[7:10])
        extended = perm[10:]
        return f"{file_type}{owner}{group}{other}{extended}"

    return "".join(CharMapping.win_file_mode.get(c, c) for c in perm)
