"""
Exception classes for Kodezi Chronos SDK
"""


class ChronosException(Exception):
    """Base exception for all Chronos errors"""
    pass


class AuthenticationError(ChronosException):
    """Raised when authentication fails"""
    pass


class RateLimitError(ChronosException):
    """Raised when rate limit is exceeded"""
    pass


class DebugTimeoutError(ChronosException):
    """Raised when debugging operation times out"""
    pass


class ValidationError(ChronosException):
    """Raised when input validation fails"""
    pass


class NetworkError(ChronosException):
    """Raised when network request fails"""
    pass


class ServerError(ChronosException):
    """Raised when server returns 5xx error"""
    pass