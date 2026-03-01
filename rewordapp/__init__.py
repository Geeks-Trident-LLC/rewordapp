"""
rewordapp: Top-level package initializer.

"""
from rewordapp.config import version
from rewordapp.core import RewordBuilder

__version__ = version

__all__ = [
    'version',
    'RewordBuilder',
]
