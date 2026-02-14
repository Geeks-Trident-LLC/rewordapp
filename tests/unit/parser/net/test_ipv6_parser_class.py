"""
Unit tests for the `rewordapp.parser.net.IPv6Parser` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/net/test_ipv6_parser.py
    or
    $ python -m pytest tests/unit/parser/net/test_ipv6_parser.py
"""

import pytest
from rewordapp.parser.net import IPv6Parser


@pytest.mark.parametrize(
    "network",
    [
        "::",
        "::a",
        "::a:b:c",
        "2701:946:200:8c1e::2dd0",
        "fe80::4ec0:79ff:fedd:d656%5",
        "2601:646:8200:8c1e:dd99:4c3f:4edc:ac40"
    ],
)
def test_generate_new(network):
    """Verify generate_new() preserves or changes octets as expected."""
    parser = IPv6Parser(network)
    new_parser = parser.generate_new()
    if parser.value == 0:
        assert new_parser.value == 0
    else:
        if len(network.strip(":").split(":")) == 1:
            assert new_parser.value == parser.value
        else:
            assert new_parser.value != parser.value


@pytest.mark.parametrize(
    "original, expected",
    [
        ("::a", "::a"),
        ("::a:b:c", "::a:b:c"),
        ("2701:946:200:8c1e::2dd0", "2701:946:200:8c1e::2dd0"),
        ("fe80::4ec0:79ff:fedd:d656%5", "fe80::4ec0:79ff:fedd:d656%30"),
        ("2601:646:8200:8c1e:dd99:4c3f:4edc:ac40", "2601:646:8200:8c1e:dd99:4c3f:4edc:ac40"),
    ],
)
def test_generate_new_produces_identical_values(original, expected):
    """IPv6Parser.generate_new() should yield identical values for identical inputs."""
    parser = IPv6Parser(original)
    other = IPv6Parser(expected)

    assert parser.generate_new().value == other.generate_new().value