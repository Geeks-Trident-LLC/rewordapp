


import pytest
from rewordapp.line import Line
import string
import re


def count_matches(pattern: str, text: str) -> int:
    """Return the number of regex matches in the given text."""
    return len(re.findall(pattern, text))


def same_lowercase_count(a: str, b: str) -> bool:
    """Check whether both strings contain the same number of lowercase letters."""
    return count_matches(r"[a-z]", a) == count_matches(r"[a-z]", b)


def same_uppercase_count(a: str, b: str) -> bool:
    """Check whether both strings contain the same number of uppercase letters."""
    return count_matches(r"[A-Z]", a) == count_matches(r"[A-Z]", b)


def same_digit_count(a: str, b: str) -> bool:
    """Check whether both strings contain the same number of digits."""
    return count_matches(r"\d", a) == count_matches(r"\d", b)


def same_whitespace(a: str, b: str) -> bool:
    """Check whether both strings contain whitespace in the same positions."""
    return re.findall(r"\s", a) == re.findall(r"\s", b)

def same_punctuation(a: str, b: str) -> bool:
    """Check whether both strings contain punctuation in the same positions."""
    punct = f"[{re.escape(string.punctuation)}]"
    return re.findall(punct, a) == re.findall(punct, b)


class TestRewordBuilder:

    @pytest.mark.parametrize(
        "data",
        [
            "Pinging td-ccm-neg-87-45.wixdns.net [34.149.87.45] with 32 bytes of data:",
            "Reply from 34.149.87.45: bytes=32 time=16ms TTL=116",
            "Ping statistics for 34.149.87.45:",
            "Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),",
            "Approximate round trip times in milli-seconds:",
            # "Minimum = 12ms, Maximum = 16ms, Average = 14ms",
        ],
    )
    def test_rewritten(self, data):
        line = Line(data)
        new = line.rewritten_content

        assert new != data
        assert len(new) == len(data)

        assert same_lowercase_count(new, data)
        assert same_uppercase_count(new, data)
        assert same_digit_count(new, data)
        assert same_whitespace(new, data)
        assert same_punctuation(new, data)
