"""Test that the public API is correctly exported from __init__."""

import skinport


class TestPublicAPI:
    def test_client_importable(self):
        assert hasattr(skinport, "Client")

    def test_salefeed_importable(self):
        assert hasattr(skinport, "SaleFeed")

    def test_exceptions_importable(self):
        assert hasattr(skinport, "SkinportError")
        assert hasattr(skinport, "SkinportAPIError")
        assert hasattr(skinport, "SkinportAuthError")
        assert hasattr(skinport, "SkinportRateLimitError")

    def test_all_is_complete(self):
        for name in skinport.__all__:
            assert hasattr(skinport, name), f"{name} in __all__ but not importable"

    def test_no_private_leaks_in_all(self):
        for name in skinport.__all__:
            assert not name.startswith("_"), f"{name} is private but in __all__"

    def test_direct_imports(self):
        from skinport import (
            Client,  # noqa: F401
            SaleFeed,  # noqa: F401
            SkinportAPIError,  # noqa: F401
            SkinportAuthError,  # noqa: F401
            SkinportError,  # noqa: F401
            SkinportRateLimitError,  # noqa: F401
        )
