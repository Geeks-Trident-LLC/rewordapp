"""
rewordapp.rewritten
===================

Utilities for generating randomized character‑substitution maps used for
rewriting or obfuscating text components such as letters, digits, and URL parts.

"""

import string
import random
import re


def build_char_map(*charsets):
    """Return a randomized one‑to‑one mapping for the given character sets."""
    mapping = {}

    for charset in charsets:
        chars = list(charset)
        shuffled = chars.copy()
        random.shuffle(shuffled)
        mapping.update(zip(chars, shuffled))

    return mapping


# Base character groups
letters_set = (string.ascii_lowercase, string.ascii_uppercase)


class CharMapping:
    """Container for randomized character‑substitution maps used for rewriting text."""

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

    @classmethod
    def refresh(cls):
        cls.first_digit = random.choice("123456789")

        """Regenerate all character‑mapping tables."""
        cls.letters = build_char_map(*letters_set)
        cls.digits = build_char_map(string.digits)
        cls.base_number = build_char_map(string.digits)
        cls.fraction_number = build_char_map(string.digits)
        cls.alphanumeric = build_char_map(*letters_set, string.digits)

        # URL‑specific mappings
        cls.url_user = build_char_map(*letters_set, string.digits)
        cls.url_host = build_char_map(*letters_set, string.digits)
        cls.url_path = build_char_map(*letters_set, string.digits)
        cls.url_query = build_char_map(*letters_set, string.digits)
        cls.url_fragment = build_char_map(*letters_set, string.digits)


def apply_mapping(source: str, mapping: dict) -> str:
    return "".join(mapping.get(ch, ch) for ch in source)

def rewrite_text(
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


def rewritten_url(user="", host="", path="", query="", fragment=""):
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


def rewrite_digits(text: str) -> str:
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


def rewrite_number(text: str) -> str:
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
        new_base = apply_mapping(base, CharMapping.base_number)
        new_fraction = apply_mapping(fraction, CharMapping.fraction_number)
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
