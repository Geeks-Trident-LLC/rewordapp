"""
rewordapp: Top-level package initializer.

This module exposes the primary classes, builders, and utilities
that form the core functionality of rewordapp. It provides access
to pattern definitions, dynamic test script generation, and
reference management utilities. End-users can leverage these
exports to build, customize, and validate regex patterns across
different contexts.
"""

from rewordapp.config import version

__version__ = version

__all__ = [
    'version',
]
