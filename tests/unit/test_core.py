from rewordapp.core import RewordBuilder

from rewordapp.deps import genericlib_dedent_and_strip as dedent_and_strip


class TestRewordBuilder:

    def test_rewritten_text(self):
        txt = dedent_and_strip("""
            Pinging td-ccm-neg-87-45.wixdns.net [34.149.87.45] with 32 bytes of data:
            Reply from 34.149.87.45: bytes=32 time=16ms TTL=116
            Reply from 34.149.87.45: bytes=32 time=16ms TTL=116
            Reply from 34.149.87.45: bytes=32 time=12ms TTL=116
            Reply from 34.149.87.45: bytes=32 time=14ms TTL=116
            
            Ping statistics for 34.149.87.45:
                Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
            Approximate round trip times in milli-seconds:
                Minimum = 12ms, Maximum = 16ms, Average = 14ms
        """)
        builder = RewordBuilder(txt)
        assert builder.rewritten_text == txt