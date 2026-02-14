"""
Unit tests for the `rewordapp.parser.net.is_valid_network` function.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/parser/net/test_is_valid_network_func.py
    or
    $ python -m pytest tests/unit/parser/net/test_is_valid_network_func.py
"""


import pytest
from rewordapp.parser.net import is_valid_network


@pytest.mark.parametrize(
    "address, expected",
    [
        ("1.1.1.1", True),
        ("192.168.0.1", True),
        ("1.1.1.1/32", True),
        ("192.168.0.1/32", True),

        ("::", True),
        ("1::", True),
        ("::1", True),
        ("1::2", True),
        ("1:2:3:4:a:b:c:d", True),
        ("1111:2222:3333:4444:aaaa:bbbb:cccc:dddd", True),

        ("::/128", True),
        ("1::/128", True),
        ("::1/128", True),
        ("1::2%128", True),
        ("1:2:3:4:a:b:c:d%128", True),
        ("1111:2222:3333:4444:aaaa:bbbb:cccc:dddd%128", True),
    ],
)
def test_valid_network(address, expected):
    """Ensure network addresses validate correctly."""
    assert is_valid_network(address) == expected


@pytest.mark.parametrize(
    "address, expected",
    [
        ("256.1.1.1", False),
        ("1.256.1.1", False),
        ("1.1.256.1", False),
        ("1.1.1.256", False),

        ("1.1.1.256/32", False),
        ("1.1.1.1/33", False),

        (":::", False),
        (":::1", False),
        ("1:::", False),
        ("1:::2", False),
        ("11111:2:3:4:5:6:7:8", False),
        ("1:22222:3:4:5:6:7:8", False),
        ("1:2:3:4:5:6:7:8:9", False),

        ("::/129", False),
        ("1::2/129", False),

    ],
)
def test_invalid_network(address, expected):
    """Ensure network addresses validate correctly."""
    assert is_valid_network(address) == expected
