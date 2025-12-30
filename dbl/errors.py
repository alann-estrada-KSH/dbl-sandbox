"""Custom exceptions for DBL"""


class DBLError(Exception):
    """Base exception for DBL errors"""
    pass


class InvalidCommandError(Exception):
    """Raised when an invalid command is provided"""
    pass
