from skinport.exceptions import (
    SkinportAPIError,
    SkinportAuthError,
    SkinportError,
    SkinportRateLimitError,
)


class TestExceptionHierarchy:
    def test_base_error(self):
        exc = SkinportError("boom")
        assert str(exc) == "boom"
        assert isinstance(exc, Exception)

    def test_api_error_inherits_base(self):
        assert issubclass(SkinportAPIError, SkinportError)

    def test_auth_error_inherits_api_error(self):
        assert issubclass(SkinportAuthError, SkinportAPIError)

    def test_rate_limit_error_inherits_api_error(self):
        assert issubclass(SkinportRateLimitError, SkinportAPIError)


class TestSkinportAPIError:
    def test_attributes(self):
        exc = SkinportAPIError(400, "Bad request")
        assert exc.status_code == 400
        assert exc.message == "Bad request"

    def test_default_message(self):
        exc = SkinportAPIError(500)
        assert "500" in exc.message

    def test_str(self):
        exc = SkinportAPIError(400, "Bad request")
        assert str(exc) == "Bad request"

    def test_repr(self):
        exc = SkinportAPIError(400)
        assert repr(exc) == "<SkinportAPIError [400]>"

    def test_auth_error_repr(self):
        exc = SkinportAuthError(401, "Unauthorized")
        assert repr(exc) == "<SkinportAuthError [401]>"


class TestSkinportRateLimitError:
    def test_without_retry_after(self):
        exc = SkinportRateLimitError()
        assert exc.status_code == 429
        assert exc.retry_after is None
        assert "Rate limit exceeded" in str(exc)

    def test_with_retry_after(self):
        exc = SkinportRateLimitError(retry_after=300)
        assert exc.retry_after == 300
        assert "300s" in str(exc)

    def test_catchable_as_api_error(self):
        exc = SkinportRateLimitError()
        assert isinstance(exc, SkinportAPIError)

    def test_catchable_as_base_error(self):
        exc = SkinportRateLimitError()
        assert isinstance(exc, SkinportError)
