"""API exceptions."""


class APIError(Exception):
    """API related errors."""


class APIConnectionError(APIError):
    """Connection errors."""


class AuthenticationError(APIError):
    """Authentication errors."""
