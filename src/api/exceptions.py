class APIError(Exception):
    pass


class APIConnectionError(APIError):
    pass


class AuthenticationError(APIError):
    pass
