"""
Unit tests for the `rewordapp.line` module.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/test_line.py
    or
    $ python -m pytest tests/unit/test_line.py
"""


import pytest
from rewordapp.line import Line

import tests.unit as testlib


class TestLineCls:

    @pytest.mark.parametrize(
        "data",
        [
            "Pinging td-ccm-neg-87-45.wixdns.net [34.149.87.45] with 32 bytes of data:",
            "Reply from 34.149.87.45: bytes=32 time=16ms TTL=116",
            "Ping statistics for 34.149.87.45:",
            "Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),",
            "Approximate round trip times in milli-seconds:",
            "Minimum = 12ms, Maximum = 16ms, Average = 14ms",
            "Link-local IPv6 Address ......... : fe80::331:b12e:54da:7225%5",
            "Physical Address. ............... : C4-BD-E5-13-0C-B3",
            "DHCPv6 Client DUID. ............. : 00-01-00-01-59-4C-58-4C-C4-1D-EA-C3-1C-23"
        ],
    )
    def test_rewritten(self, data):
        line = Line(data)
        new = line.rewritten
        assert new != data
        assert len(new) == len(data)

        assert testlib.same_lowercase_count(new, data)
        assert testlib.same_uppercase_count(new, data)
        assert testlib.same_digit_count(new, data)
        assert testlib.same_whitespace(new, data)
        assert testlib.same_punctuation(new, data)


    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                "Pinging td-ccm-neg-87-45.wixdns.net [34.149.87.45] with ...",
                (
                    "WordToken",
                    "WhitespaceToken",
                    "URLToken",
                    "WhitespaceToken",
                    "IPv4Token",
                    "WhitespaceToken",
                    "WordToken",
                    "WhitespaceToken",
                    "FallbackToken",
                )
             ),
            (
                "Reply from 34.149.87.45: bytes=32 ...",
                (
                    "WordToken",
                    "WhitespaceToken",
                    "WordToken",
                    "WhitespaceToken",
                    "IPv4Token",
                    "WhitespaceToken",
                    "WordToken",
                    "WhitespaceToken",
                    "FallbackToken",
                ),
            ),
            (
                "Packets: Sent = 4, ... (0% loss),",
                (
                    "WordToken",
                    "WhitespaceToken",
                    "WordToken",
                    "WhitespaceToken",
                    "FallbackToken",
                    "WhitespaceToken",
                    "NumberToken",
                    "WhitespaceToken",
                    "FallbackToken",
                    "WhitespaceToken",
                    "NumberToken",
                    "WhitespaceToken",
                    "WordToken",
                )
            ),
            (
                "Minimum = 12ms, Maximum = 16ms, ...",
                (
                    "WordToken",
                    "WhitespaceToken",
                    "FallbackToken",
                    "WhitespaceToken",
                    "NumberToken",
                    "WhitespaceToken",
                    "WordToken",
                    "WhitespaceToken",
                    "FallbackToken",
                    "WhitespaceToken",
                    "NumberToken",
                    "WhitespaceToken",
                    "FallbackToken",
                )
            ),
            (
                "Link-local IPv6 Address ......... : fe80::331:b12e:54da:7225%5",
                (
                    "WordToken",
                    "WhitespaceToken",
                    "WordToken",
                    "WhitespaceToken",
                    "WordToken",
                    "WhitespaceToken",
                    "FallbackToken",
                    "WhitespaceToken",
                    "FallbackToken",
                    "WhitespaceToken",
                    "IPv6Token"
                )
            ),
            (
                "Physical Address. ............... : C4-BD-E5-13-0C-B3",
                (
                    "WordToken",
                    "WhitespaceToken",
                    "WordToken",
                    "WhitespaceToken",
                    "FallbackToken",
                    "WhitespaceToken",
                    "FallbackToken",
                    "WhitespaceToken",
                    "MACToken",
                )
            ),
            (
                "DHCPv6 Client DUID. ............. : 00-01-00-01-59-4C-58-4C-C4-1D-EA-C3-1C-23",
                (
                    "WordToken",
                    "WhitespaceToken",
                    "WordToken",
                    "WhitespaceToken",
                    "WordToken",
                    "WhitespaceToken",
                    "FallbackToken",
                    "WhitespaceToken",
                    "FallbackToken",
                    "WhitespaceToken",
                    "MACToken",
                )
            )

        ],
    )
    def test_tokenize(self, data, expected):
        line = Line(data)
        tokens = line.tokenize()
        tokens_names = [type(token).__name__ for token in tokens]
        for index, token_name in enumerate(tokens_names):
            assert token_name in expected[index]
