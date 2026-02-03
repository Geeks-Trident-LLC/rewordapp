import pytest
from rewordapp.line import Line


class TestRewordBuilder:

    @pytest.mark.parametrize(
        "line, expected",
        [
            (
                "Pinging td-ccm-neg-87-45.wixdns.net [34.149.87.45] with 32 bytes of data:",
                "Pinging td-ccm-neg-87-45.wixdns.net [34.149.87.45] with 32 bytes of data:"
            ),
            (
                "Reply from 34.149.87.45: bytes=32 time=16ms TTL=116",
                "Reply from 34.149.87.45: bytes=32 time=16ms TTL=116"
            ),
            (
                "Ping statistics for 34.149.87.45:",
                "Ping statistics for 34.149.87.45:"
            ),
            (
                "Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),",
                "Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),"
            ),
            (
                "Approximate round trip times in milli-seconds:",
                "Approximate round trip times in milli-seconds:"
            ),
            (
                "Minimum = 12ms, Maximum = 16ms, Average = 14ms",
                "Minimum = 12ms, Maximum = 16ms, Average = 14ms"
            ),
        ],
    )
    def test_rewritten(self, line, expected):
        line = Line(line)
        assert line.rewritten == expected