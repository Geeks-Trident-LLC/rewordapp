"""
rewordapp.exceptions
====================

Exception classes for the rewordapp project.
"""


class InvalidRulesFormat(Exception):
    """
    Raised when the rules format is invalid.
    """


class RewriteRuleError(Exception):
    """Base exception for rewrite rule validation and processing errors."""


class DateTimeRuleError(RewriteRuleError):
    """Raised when datetime rewrite rules are invalid or cannot be applied."""


class UnchangedLinesError(RewriteRuleError):
    """Raised when unchanged lines are invalid or cannot be applied."""