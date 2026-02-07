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
