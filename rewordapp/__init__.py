"""
rewordapp: Top-level package initializer.

"""
import string
import re
from rewordapp.config import version

__version__ = version

__all__ = [
    'version',
]


class PATTERN:
    punct = rf"[{re.escape(string.punctuation)}]"
    puncts = rf"{punct}+"