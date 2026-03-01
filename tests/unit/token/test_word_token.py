"""
Unit tests for the `rewordapp.core.token.WordToken` class.

Usage
-----
Run pytest in the project root to execute these tests:
    $ pytest tests/unit/token/test_word_token.py
    or
    $ python -m pytest tests/unit/token/test_word_token.py
"""


from rewordapp.core.token import WordToken


def test_word_token_preserves_length():
    """Ensure WordToken.rewritten keeps the same character count."""
    original = "you’re"
    token = WordToken(original)

    assert len(token.rewritten) == len(original)
