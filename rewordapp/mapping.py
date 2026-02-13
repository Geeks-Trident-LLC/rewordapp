"""
rewordapp.mapping
=================

Provides the character‑mapping infrastructure for RewordApp.
"""

import random
import re
from string import digits, ascii_lowercase, ascii_uppercase

from rewordapp.deps import genericlib_DotObject as DotObject


def refresh() -> None:
    """Refresh all character‑mapping tables."""
    Mapping.refresh()


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
            Mapping.octal.get(ch, ch) for ch in text[prefix_len:]
        )

    # Default: apply generic mapping
    return "".join(mapping.get(ch, ch) for ch in text)


class Mapping:
    """Container for randomized character‑substitution maps used for rewriting text."""

    # Base character groups
    letters_set = (
        "ae", "bcdf", "iou", "y","ghjklmnpqrstvwxz",
        "AE", "BCDF", "IOU", "Y","GHJKLMNPQRSTVWXZ"
    )
    first_digit = random.choice(digits[1:])
    digits_set = (digits[:1], digits[1:])
    hex_set = (ascii_lowercase[:6], ascii_uppercase[:6], *digits_set)
    alphanumeric_set = (*letters_set, *digits_set)

    # General mappings
    letters = build_char_map(*letters_set)
    base_number = build_char_map(*digits_set)
    fraction_number = build_char_map(*digits_set)
    alphanumeric = build_char_map(*alphanumeric_set)
    octal = build_char_map(digits[:1], digits[1:-2])
    file_permission = build_char_map(digits[:8])
    win_file_mode = build_char_map("-", "d", "D", "ahilrs", "AHILRS")

    # URL‑specific mappings
    url = DotObject(
        user=build_char_map(*alphanumeric_set),
        host=build_char_map(*alphanumeric_set),
        path=build_char_map(*alphanumeric_set),
        query=build_char_map(*alphanumeric_set),
        fragment=build_char_map(*alphanumeric_set)
    )

    # MAC address mapping
    mac_octet = build_char_map(*hex_set)

    # IPv4 address mapping
    ipv4_octet = build_ipv4_octet_map()

    # IPv6 address mapping
    ipv6_octet = build_char_map(*hex_set)

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
        cls.win_file_mode = build_char_map("-", "d", "D", "ahilrs", "AHILRS")

        # URL‑specific mappings
        cls.url = DotObject(
            user=build_char_map(*cls.alphanumeric_set),
            host=build_char_map(*cls.alphanumeric_set),
            path=build_char_map(*cls.alphanumeric_set),
            query=build_char_map(*cls.alphanumeric_set),
            fragment=build_char_map(*cls.alphanumeric_set)
        )

        # MAC address mapping
        cls.mac_octet = build_char_map(*cls.hex_set)

        # IPv4 address mapping
        cls.ipv4_octet = build_ipv4_octet_map()

        # IPv6 address mapping
        cls.ipv6_octet = build_char_map(*cls.hex_set)
