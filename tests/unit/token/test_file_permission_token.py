"""
Unit tests for the `rewordapp.core.token.FilePermissionToken` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/token/test_file_permission_token.py
    or
    $ python -m pytest tests/unit/token/test_file_permission_token.py
"""

import pytest
from rewordapp.core.token import FilePermissionToken


@pytest.mark.parametrize(
    "fperm, expected",
    [
        # linux file permission
        ("----------", True),
        ("drwxr-xr-x", True),
        ("-rw-r--r--", True),
        ("lrw-r--r--", True),
        ("crw-r--r--", True),
        ("brw-r--r--", True),
        ("srw-r--r--", True),
        ("wrw-r--r--", True),
        ("Drw-r--r--", True),

        ("-rwtr--r-S", True),
        ("-rw-r-tr-s", True),
        ("-rw-r-tr-t", True),
        ("-rw-r-tr-T", True),

        ("-rw-r--r--@", True),
        ("drwxr-xr-x+", True),
        ("-rw-r--r--.", True),

        ("erw-r--r--", False),
        ("-rwar--r--", False),

        # Windows file attribute
        ("------", True),
        ("d-----", True),
        ("-a----", True),

        ("-a---", False),
        ("-a-----", False)

    ],
)
def test_file_permission_token(fperm, expected):
    """Ensure FilePermissionToken.rewritten keeps the same character count."""
    token = FilePermissionToken(fperm)
    rewritten = token.rewritten
    assert bool(token) == expected
    if token:
        assert len(rewritten) == len(fperm)
