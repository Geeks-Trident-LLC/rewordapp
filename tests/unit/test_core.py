
import pytest
from rewordapp.core import RewordBuilder

from rewordapp.deps import genericlib_dedent_and_strip as dedent_and_strip


class TestRewordBuilder:

    @pytest.mark.parametrize(
        "txt",
        [
            """
            Pinging td-ccm-neg-87-45.wixdns.net [34.149.87.45] with 32 bytes of data:
            Reply from 34.149.87.45: bytes=32 time=16ms TTL=116
            Reply from 34.149.87.45: bytes=32 time=16ms TTL=116
            Reply from 34.149.87.45: bytes=32 time=12ms TTL=116
            Reply from 34.149.87.45: bytes=32 time=14ms TTL=116
            
            Ping statistics for 34.149.87.45:
                Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
            Approximate round trip times in milli-seconds:
                Minimum = 12ms, Maximum = 16ms, Average = 14ms
            """,
            r"""
            Server:  cdns01.comcast.net
            Address:  2001:558:feed::1
            
            Non-authoritative answer:
            Name:    ad-edm-mbg-67-13.wixdns.net
            Address:  25.137.36.54
            Aliases:  www.geekstrident.com
                      cdn1.wixdns.net
            """
        ],
    )
    def test_rewritten_text(self, txt):
        text = dedent_and_strip(txt)
        builder = RewordBuilder(text)
        rewritten = builder.rewritten
        assert rewritten != text
        assert len(rewritten) == len(text)