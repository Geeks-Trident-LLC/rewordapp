"""
Unit tests for the `rewordapp.rewritten.new_mac_address` function.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/rewrite/test_new_mac_address.py
    or
    $ python -m pytest tests/unit/rewrite/test_new_mac_address.py
"""

import pytest
import rewordapp.rewrite.rewritten as rewritten


@pytest.mark.parametrize(
    "mac_address, expected",
    [
        ("11:22:33:aa:bb:cc", "11:22:33"),
        ("11-22-33-aa-bb-cc", "11-22-33"),
        ("112233aabbcc", "112233"),
        ("11 22 33 aa bb cc", "11 22 33"),
        ("112.233.aab.bcc", "112.233"),

    ],
)
def test_mac_address(mac_address, expected):
    new_mac_address = rewritten.new_mac_address(mac_address)
    assert new_mac_address.startswith(expected) is True
    assert new_mac_address != mac_address