"""Exception hierarchy for the skinport library.

All exceptions inherit from :class:`SkinportError`, making it easy
to catch any library-specific error with a single except clause.
"""


class SkinportError(Exception):
    """Base exception for all skinport errors."""


class SkinportAPIError(SkinportError):
    """Raised when the API returns a non-200 response.

    :param status_code: HTTP status code from the API.
    :param message: human-readable error message.
    """

    def __init__(self, status_code: int, message: str | None = None) -> None:
        self.status_code = status_code
        self.message = message or f"API request failed with status {status_code}"
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} [{self.status_code}]>"


class SkinportAuthError(SkinportAPIError):
    """Raised on authentication or authorization failures (401, 403)."""


class SkinportRateLimitError(SkinportAPIError):
    """Raised when the API rate limit is exceeded (429).

    :param retry_after: seconds to wait before retrying, if provided
        by the API via the ``Retry-After`` header.
    """

    def __init__(self, retry_after: float | None = None) -> None:
        self.retry_after = retry_after
        message = "Rate limit exceeded"
        if retry_after is not None:
            message += f", retry after {retry_after}s"
        super().__init__(429, message)
