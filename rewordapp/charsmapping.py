"""
rewordapp.charsmapping
======================

Utilities for generating randomized character‑substitution maps used for
rewriting or obfuscating text components such as letters, digits, and URL parts.

"""

import string
import random


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
    alphanum = build_char_map(*letters_set, string.digits)

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
        cls.alphanum = build_char_map(*letters_set, string.digits)

        # URL‑specific mappings
        cls.url_user = build_char_map(*letters_set, string.digits)
        cls.url_host = build_char_map(*letters_set, string.digits)
        cls.url_path = build_char_map(*letters_set, string.digits)
        cls.url_query = build_char_map(*letters_set, string.digits)
        cls.url_fragment = build_char_map(*letters_set, string.digits)


def apply_mapping(source: str, mapping: dict) -> str:
    return "".join(mapping.get(ch, ch) for ch in source)

def rewrite_text(
        txt: str,
        *,
        letters=False,
        alphanumeric=False,
        digits=False,
        number=False,
):
    """Return a rewritten version of the text using the selected character mapping."""

    if not txt.strip():
        return txt

    if letters:
        return apply_mapping(txt, CharMapping.letters)
    if digits:
        return apply_mapping(txt, CharMapping.digits)
    if number:
        # Preserve fractional structure if present
        if "." in txt:
            base, fraction = txt.rsplit(".", maxsplit=1)
            new_base = apply_mapping(base, CharMapping.base_number)
            new_fraction = apply_mapping(base, CharMapping.fraction_number)
            return f"{new_base}.{new_fraction}"
        return apply_mapping(txt, CharMapping.base_number)
    if alphanumeric:
        return apply_mapping(txt, CharMapping.alphanum)

    return txt


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
