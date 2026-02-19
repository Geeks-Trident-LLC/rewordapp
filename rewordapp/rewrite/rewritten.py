"""
rewordapp.rewrite.rewritten
===========================

Utilities for generating randomized character‑substitution maps used for
rewriting or obfuscating text components such as letters, digits, and URL parts.

"""

import string
import re
import ipaddress

from rewordapp import utils
from rewordapp.rewrite import checker
from rewordapp.rewrite.checker import has_known_extension
from rewordapp.rewrite.mapping import generate_random_binary, Mapping, apply_mapping


def new_word(text: str) -> str:
    """Rewrite a word while preserving punctuation and applying
    the appropriate character mapping."""
    if not text.strip():
        return text

    # Choose mapping based on whether the segment is pure letters
    def select_mapping(segment: str):
        if re.fullmatch(r"[A-Za-z]", segment):
            return Mapping.letters
        return Mapping.alphanumeric

    punct_pattern = f"[{re.escape(string.punctuation)}]"

    ext_pattern = rf'''(?ixu)
            [^\\/:*?"><|][.]
            (?P<last>(?P<ext>[a-z0-9][a-z0-9_-]*)
            {punct_pattern}*)$
        '''
    first = text
    last = ""
    match = re.search(ext_pattern, text)
    if match:
        ext = match.group("ext")
        if checker.has_known_extension(ext):
            last = match.group("last")
            first = text[:-len(last)]

    parts = []
    for item in utils.split_by_matches(first, f"{punct_pattern}+"):
        parts.append(apply_mapping(item, select_mapping(item)))
    return "".join(parts) + last


def new_url(user="", host="", path="", query="", fragment=""):
    """Rewrite a single URL component using the appropriate character mapping."""
    # User component
    if user:
        return apply_mapping(user, Mapping.url.user)

    # Host component (preserve TLD)
    if host:
        if host.count(".") == 0:
            return apply_mapping(host, Mapping.url.host)

        if host.count(".") == 1:
            domain, tld = host.rsplit(".", maxsplit=1)
            rewritten = apply_mapping(domain, Mapping.url.host)
            return f"{rewritten}.{tld}"
        subdomain, *other, tld = host.split(".")
        rewritten = apply_mapping(".".join(other), Mapping.url.host)
        # if re.fullmatch(r"(?i)[a-z][a-z0-9]+", subdomain):
        #     return f"{subdomain}.{rewritten}.{tld}"

        if checker.has_common_subdomain(host):
            return f"{subdomain}.{rewritten}.{tld}"

        rewritten_subdomain = apply_mapping(subdomain, Mapping.url.host)
        return f"{rewritten_subdomain}.{rewritten}.{tld}"


    # Determine which component is present
    if path:
        data, mapping = path, Mapping.url.path
    elif query:
        data, mapping = query, Mapping.url.query
    elif fragment:
        data, mapping = fragment, Mapping.url.fragment
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
            else apply_mapping(base, Mapping.base_number)

        new_fraction = fraction if (fraction.isdigit() and int(fraction) == 0) \
            else apply_mapping(fraction, Mapping.fraction_number)

        rewritten = f"{new_base}.{new_fraction}"

        # Avoid leading zero in multi‑digit results
        if re.match(r"0[0-9]", rewritten):
            return f"{Mapping.first_digit}{rewritten[1:]}"

        return rewritten

    # binary
    if re.fullmatch("0[01]+", text):
        return generate_random_binary(text)

    # octal
    if re.fullmatch("0[0-7]+", text):
        return apply_mapping(text, Mapping.octal)

    # generic integer
    rewritten = apply_mapping(text, Mapping.base_number)
    if re.match(r"0[0-9]", rewritten):
        return f"{Mapping.first_digit}{rewritten[1:]}"

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
        mapped = apply_mapping(octet, Mapping.mac_octet)
        rewritten.append(mapped)

    return sep.join(rewritten)


def new_ipv4_address(address: str) -> str:
    """Rewrite an IPv4 address by remapping octets 2–4 using predefined mappings."""
    octets = address.strip().split(".")
    if len(octets) != 4:
        return address

    first_octet = octets[0]
    new_octets = []
    if all(octet == first_octet for octet in octets):
        new_octets = [Mapping.ipv4_octet.get(first_octet, first_octet)] * 4
    else:
        for idx, octet in enumerate(octets):
            if idx == 0 or octet == first_octet:
                new_octets.append(first_octet)
            else:
                new_octets.append(Mapping.ipv4_octet.get(octet, octet))
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
            mapped = apply_mapping(group, Mapping.ipv6_octet)
            rewritten.append(mapped)
        else:
            rewritten.append(group)
            # Begin rewriting after the first non‑zero group
            if group.strip("0"):
                rewrite_started = True

    compressed = ipaddress.ip_address(":".join(rewritten)).compressed
    return compressed.upper() if is_uppercase else compressed


def new_file_permission(perm: str) -> str:
    """Rewrite owner/group/other permission bits using mapped patterns."""
    def remap(bits: str) -> str:
        original = bits
        value = int("".join("0" if c == "-" else "1" for c in bits), 2)
        new_value = int(Mapping.file_permission.get(str(value), str(value)))

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

    return "".join(Mapping.win_file_mode.get(c, c) for c in perm)
