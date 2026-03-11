import base64
import time
from unittest.mock import MagicMock, patch

import pytest

from skinport import Client
from skinport.client import _RateLimiter
from skinport.exceptions import (
    SkinportAPIError,
    SkinportAuthError,
    SkinportRateLimitError,
)
from tests.conftest import make_response

# -- construction and repr -------------------------------------------------


class TestClientInit:
    def test_anonymous(self, client):
        assert client._client_id is None
        assert client._client_secret is None

    def test_authenticated(self, auth_client):
        assert auth_client._client_id == "test_id"
        assert auth_client._client_secret == "test_secret"

    def test_custom_base_url(self):
        c = Client(base_url="https://custom.api/v1/")
        assert c.base_url == "https://custom.api/v1/"

    def test_default_base_url(self, client):
        assert client.base_url == "https://api.skinport.com/v1/"

    def test_repr_anonymous(self, client):
        assert repr(client) == "<skinport.Client [anonymous]>"

    def test_repr_authenticated(self, auth_client):
        assert repr(auth_client) == "<skinport.Client [authenticated]>"

    def test_context_manager(self):
        with Client() as c:
            assert isinstance(c, Client)

    def test_context_manager_closes_on_exit(self):
        c = Client()
        c._session = MagicMock()
        c.__exit__(None, None, None)
        c._session.close.assert_called_once()

    def test_context_manager_closes_on_exception(self):
        c = Client()
        c._session = MagicMock()
        try:
            with c:
                raise ValueError("boom")
        except ValueError:
            pass
        c._session.close.assert_called_once()

    def test_close(self):
        c = Client()
        c._session = MagicMock()
        c.close()
        c._session.close.assert_called_once()

    def test_accept_encoding_header(self, client):
        assert "br" in client._session.headers["Accept-Encoding"]

    def test_user_agent_header(self, client):
        assert "skinport/" in client._session.headers["User-Agent"]

    def test_sales_namespace(self, client):
        assert hasattr(client, "sales")
        assert hasattr(client.sales, "history")
        assert hasattr(client.sales, "out_of_stock")

    def test_account_namespace(self, client):
        assert hasattr(client, "account")
        assert hasattr(client.account, "transactions")

    def test_keyword_only_args(self):
        with pytest.raises(TypeError):
            Client("id", "secret")  # positional args not allowed

    def test_two_clients_independent(self):
        c1 = Client(client_id="a", client_secret="b")
        c2 = Client(client_id="x", client_secret="y")
        assert c1._client_id != c2._client_id
        assert c1._session is not c2._session


# -- auth ------------------------------------------------------------------


class TestAuth:
    def test_token_encoding(self, auth_client):
        headers = auth_client._auth_headers()
        token = headers["Authorization"].removeprefix("Basic ")
        decoded = base64.b64decode(token).decode()
        assert decoded == "test_id:test_secret"

    def test_only_client_id_raises(self):
        c = Client(client_id="id_only")
        with pytest.raises(SkinportAuthError, match="client_id and client_secret"):
            c._auth_headers()

    def test_only_client_secret_raises(self):
        c = Client(client_secret="secret_only")
        with pytest.raises(SkinportAuthError, match="client_id and client_secret"):
            c._auth_headers()

    def test_special_chars_in_credentials(self):
        c = Client(client_id="user@host", client_secret="p@ss:word!")
        headers = c._auth_headers()
        token = headers["Authorization"].removeprefix("Basic ")
        decoded = base64.b64decode(token).decode()
        assert decoded == "user@host:p@ss:word!"


# -- namespace binding -----------------------------------------------------


class TestNamespaceBinding:
    def test_sales_shares_client_request(self, client):
        assert client.sales._request == client._request

    def test_account_shares_client_request(self, client):
        assert client.account._request == client._request

    def test_sales_uses_client_session(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])
        client.sales.history()
        client._session.request.assert_called_once()

    def test_account_uses_client_session(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            json_data={"data": [], "pagination": {}},
        )
        auth_client.account.transactions()
        auth_client._session.request.assert_called_once()


# -- public endpoints ------------------------------------------------------


class TestItems:
    def test_default_params(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            json_data=[{"market_hash_name": "AK-47"}],
        )
        result = client.items()

        assert result == [{"market_hash_name": "AK-47"}]
        client._session.request.assert_called_once_with(
            "GET",
            "https://api.skinport.com/v1/items",
            params={"app_id": 730, "currency": "EUR", "tradable": "true"},
            headers={},
            timeout=30,
        )

    def test_custom_params(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])

        client.items(app_id=440, currency="USD", tradable=False)

        call_kwargs = client._session.request.call_args
        assert call_kwargs[1]["params"] == {
            "app_id": 440,
            "currency": "USD",
            "tradable": "false",
        }

    def test_tradable_false_serialization(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])
        client.items(tradable=False)
        params = client._session.request.call_args[1]["params"]
        assert params["tradable"] == "false"

    def test_tradable_true_serialization(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])
        client.items(tradable=True)
        params = client._session.request.call_args[1]["params"]
        assert params["tradable"] == "true"

    def test_no_auth_header_sent(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])

        client.items()

        call_kwargs = client._session.request.call_args
        assert call_kwargs[1]["headers"] == {}

    def test_url_construction_with_custom_base(self):
        c = Client(base_url="https://test.example.com/v2/")
        c._session = MagicMock()
        c._session.request.return_value = make_response(json_data=[])
        c.items()
        url = c._session.request.call_args[0][1]
        assert url == "https://test.example.com/v2/items"


class TestSalesHistory:
    def test_default_params(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])

        client.sales.history()

        call_kwargs = client._session.request.call_args
        assert call_kwargs[1]["params"] == {
            "app_id": 730,
            "currency": "EUR",
        }

    def test_with_market_hash_name(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])

        client.sales.history(
            market_hash_name="AK-47 | Redline (Field-Tested)",
        )

        call_kwargs = client._session.request.call_args
        assert call_kwargs[1]["params"]["market_hash_name"] == (
            "AK-47 | Redline (Field-Tested)"
        )

    def test_market_hash_name_omitted_when_none(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])
        client.sales.history()
        params = client._session.request.call_args[1]["params"]
        assert "market_hash_name" not in params

    def test_multiple_items_comma_delimited(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])
        names = "Glove Case Key,★ Karambit | Slaughter (Minimal Wear)"
        client.sales.history(market_hash_name=names)
        params = client._session.request.call_args[1]["params"]
        assert params["market_hash_name"] == names

    def test_no_auth_header(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])

        client.sales.history()

        call_kwargs = client._session.request.call_args
        assert call_kwargs[1]["headers"] == {}

    def test_correct_url_path(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])
        client.sales.history()
        url = client._session.request.call_args[0][1]
        assert url.endswith("sales/history")


class TestSalesOutOfStock:
    def test_default_params(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])

        client.sales.out_of_stock()

        call_kwargs = client._session.request.call_args
        assert call_kwargs[1]["params"] == {
            "app_id": 730,
            "currency": "EUR",
        }

    def test_custom_params(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])

        client.sales.out_of_stock(app_id=252490, currency="USD")

        call_kwargs = client._session.request.call_args
        assert call_kwargs[1]["params"] == {
            "app_id": 252490,
            "currency": "USD",
        }

    def test_no_auth_header(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])
        client.sales.out_of_stock()
        assert client._session.request.call_args[1]["headers"] == {}

    def test_correct_url_path(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])
        client.sales.out_of_stock()
        url = client._session.request.call_args[0][1]
        assert url.endswith("sales/out-of-stock")


# -- authenticated endpoints -----------------------------------------------


class TestAccountTransactions:
    def test_default_params(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            json_data={"data": [], "pagination": {}},
        )
        result = auth_client.account.transactions()

        assert result == {"data": [], "pagination": {}}
        call_kwargs = auth_client._session.request.call_args
        assert call_kwargs[1]["params"] == {
            "page": 1,
            "limit": 100,
            "order": "desc",
        }

    def test_custom_params(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            json_data={"data": [], "pagination": {}},
        )
        auth_client.account.transactions(page=2, limit=10, order="asc")

        call_kwargs = auth_client._session.request.call_args
        assert call_kwargs[1]["params"] == {
            "page": 2,
            "limit": 10,
            "order": "asc",
        }

    def test_sends_auth_header(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            json_data={"data": [], "pagination": {}},
        )
        auth_client.account.transactions()

        call_kwargs = auth_client._session.request.call_args
        headers = call_kwargs[1]["headers"]
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")

    def test_no_credentials_raises(self, client):
        with pytest.raises(SkinportAuthError, match="client_id and client_secret"):
            client.account.transactions()

    def test_correct_url_path(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            json_data={"data": [], "pagination": {}},
        )
        auth_client.account.transactions()
        url = auth_client._session.request.call_args[0][1]
        assert url.endswith("account/transactions")


# -- error handling --------------------------------------------------------


class TestErrorHandling:
    def test_api_error_generic(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=500,
            text="Internal Server Error",
        )
        with pytest.raises(SkinportAPIError) as exc_info:
            client.items()
        assert exc_info.value.status_code == 500

    def test_api_error_with_json_message(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=400,
            json_data={"message": "Invalid currency"},
        )
        with pytest.raises(SkinportAPIError, match="Invalid currency"):
            client.items()

    def test_api_error_with_error_key(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=400,
            json_data={"error": "Bad request"},
        )
        with pytest.raises(SkinportAPIError, match="Bad request"):
            client.items()

    def test_api_error_message_key_takes_precedence(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=400,
            json_data={"message": "Specific error", "error": "Generic error"},
        )
        with pytest.raises(SkinportAPIError, match="Specific error"):
            client.items()

    def test_api_error_falls_back_to_text(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=500,
            text="Plain text error",
        )
        with pytest.raises(SkinportAPIError) as exc_info:
            client.items()
        assert exc_info.value.message == "Plain text error"

    def test_auth_error_401(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            status_code=401,
            text="Unauthorized",
        )
        with pytest.raises(SkinportAuthError):
            auth_client.account.transactions()

    def test_auth_error_403(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            status_code=403,
            text="Forbidden",
        )
        with pytest.raises(SkinportAuthError):
            auth_client.account.transactions()

    def test_auth_error_is_catchable_as_api_error(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            status_code=401,
            text="Unauthorized",
        )
        with pytest.raises(SkinportAPIError):
            auth_client.account.transactions()

    def test_rate_limit_error(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=429,
            headers={},
            text="",
        )
        with pytest.raises(SkinportRateLimitError) as exc_info:
            client.items()
        assert exc_info.value.retry_after is None

    def test_rate_limit_error_with_retry_after(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=429,
            headers={"Retry-After": "300"},
            text="",
        )
        with pytest.raises(SkinportRateLimitError) as exc_info:
            client.items()
        assert exc_info.value.retry_after == 300.0

    def test_rate_limit_is_catchable_as_api_error(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=429,
            headers={},
            text="",
        )
        with pytest.raises(SkinportAPIError):
            client.items()

    def test_error_with_empty_response(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=502,
            text="",
        )
        with pytest.raises(SkinportAPIError) as exc_info:
            client.items()
        assert exc_info.value.status_code == 502

    def test_success_with_invalid_json_raises(self, client):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.side_effect = ValueError("bad json")
        client._session = MagicMock()
        client._session.request.return_value = resp
        with pytest.raises(SkinportAPIError, match="invalid JSON"):
            client.items()

    def test_error_via_sales_namespace(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=500,
            text="Server Error",
        )
        with pytest.raises(SkinportAPIError):
            client.sales.history()

    def test_error_via_account_namespace(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            status_code=500,
            text="Server Error",
        )
        with pytest.raises(SkinportAPIError):
            auth_client.account.transactions()

    def test_api_error_with_errors_array(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=401,
            json_data={
                "errors": [
                    {
                        "id": "authentication_error",
                        "message": "Authentication is missing or invalid.",
                    }
                ]
            },
        )
        with pytest.raises(
            SkinportAPIError, match="Authentication is missing or invalid"
        ):
            client.items()

    def test_unmapped_4xx_raises_generic_api_error(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=418,
            text="I'm a teapot",
        )
        with pytest.raises(SkinportAPIError) as exc_info:
            client.items()
        assert exc_info.value.status_code == 418
        assert not isinstance(exc_info.value, SkinportAuthError)
        assert not isinstance(exc_info.value, SkinportRateLimitError)


# -- session reuse ---------------------------------------------------------


class TestSessionReuse:
    def test_multiple_requests_reuse_session(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])

        client.items()
        client.sales.history()
        client.sales.out_of_stock()

        assert client._session.request.call_count == 3


# -- rate limiter ----------------------------------------------------------


class TestRateLimiter:
    def test_allows_requests_under_limit(self):
        limiter = _RateLimiter(max_requests=3, window=10.0)
        for _ in range(3):
            limiter.acquire("group")
        # No sleep, no error — all three fit in the window.

    def test_sleeps_when_at_limit(self):
        limiter = _RateLimiter(max_requests=2, window=1.0)
        limiter.acquire("g")
        limiter.acquire("g")
        with patch("skinport.client.time.sleep") as mock_sleep:
            with patch("skinport.client.time.monotonic") as mock_mono:
                # First two timestamps at t=100, t=100.
                # Third acquire sees window full, oldest at t=100,
                # so sleep_for = 100 + 1.0 - 100.5 = 0.5
                calls = iter([100.5, 101.0, 101.0])
                mock_mono.side_effect = lambda: next(calls)
                # Replace the existing timestamps with known values.
                limiter._history["g"] = __import__("collections").deque(
                    [100.0, 100.0]
                )
                limiter.acquire("g")
            mock_sleep.assert_called_once()
            slept = mock_sleep.call_args[0][0]
            assert slept == pytest.approx(0.5, abs=0.01)

    def test_independent_groups(self):
        limiter = _RateLimiter(max_requests=1, window=100.0)
        limiter.acquire("items")
        # Different group should not be blocked.
        with patch("skinport.client.time.sleep") as mock_sleep:
            limiter.acquire("sales")
        mock_sleep.assert_not_called()

    def test_window_expiry_frees_slots(self):
        limiter = _RateLimiter(max_requests=1, window=0.05)
        limiter.acquire("g")
        time.sleep(0.06)
        # Slot should be freed after the window expires.
        with patch("skinport.client.time.sleep") as mock_sleep:
            limiter.acquire("g")
        mock_sleep.assert_not_called()


class TestClientRateLimiting:
    def test_rate_limit_enabled_by_default(self):
        c = Client()
        assert c._limiter is not None

    def test_rate_limit_disabled(self):
        c = Client(rate_limit=False)
        assert c._limiter is None

    def test_limiter_called_on_request(self):
        c = Client()
        c._limiter = MagicMock()
        c._session = MagicMock()
        c._session.request.return_value = make_response(json_data=[])
        c.items()
        c._limiter.acquire.assert_called_once_with("items")

    def test_limiter_groups_sales_endpoints(self):
        c = Client()
        c._limiter = MagicMock()
        c._session = MagicMock()
        c._session.request.return_value = make_response(json_data=[])
        c.sales.history()
        c.sales.out_of_stock()
        calls = [call[0][0] for call in c._limiter.acquire.call_args_list]
        assert calls == ["sales", "sales"]

    def test_limiter_groups_account_endpoints(self):
        c = Client(client_id="id", client_secret="secret")
        c._limiter = MagicMock()
        c._session = MagicMock()
        c._session.request.return_value = make_response(
            json_data={"data": [], "pagination": {}},
        )
        c.account.transactions()
        c._limiter.acquire.assert_called_once_with("account")

    def test_no_limiter_call_when_disabled(self):
        c = Client(rate_limit=False)
        c._session = MagicMock()
        c._session.request.return_value = make_response(json_data=[])
        c.items()
        # No limiter to call — just verifying no AttributeError.

    def test_default_client_has_real_limiter(self):
        c = Client()
        assert isinstance(c._limiter, _RateLimiter)

    def test_default_client_acquire_called_on_request(self):
        c = Client()
        c._session = MagicMock()
        c._session.request.return_value = make_response(json_data=[])
        with patch.object(_RateLimiter, "acquire", autospec=True) as spy:
            c.items()
        spy.assert_called_once_with(c._limiter, "items")


# -- timeout ---------------------------------------------------------------


class TestTimeout:
    def test_default_timeout(self):
        c = Client()
        assert c.timeout == 30

    def test_custom_timeout(self):
        c = Client(timeout=60)
        assert c.timeout == 60

    def test_timeout_none_disables(self):
        c = Client(timeout=None)
        assert c.timeout is None

    def test_timeout_passed_to_request(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])
        client.items()
        call_kwargs = client._session.request.call_args[1]
        assert call_kwargs["timeout"] == 30

    def test_custom_timeout_passed_to_request(self):
        c = Client(timeout=10, rate_limit=False)
        c._session = MagicMock()
        c._session.request.return_value = make_response(json_data=[])
        c.items()
        call_kwargs = c._session.request.call_args[1]
        assert call_kwargs["timeout"] == 10

    def test_none_timeout_passed_to_request(self):
        c = Client(timeout=None, rate_limit=False)
        c._session = MagicMock()
        c._session.request.return_value = make_response(json_data=[])
        c.items()
        call_kwargs = c._session.request.call_args[1]
        assert call_kwargs["timeout"] is None


# -- retry-after parsing ---------------------------------------------------


class TestRetryAfterParsing:
    def test_malformed_retry_after_does_not_crash(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=429,
            headers={"Retry-After": "not-a-number"},
            text="",
        )
        with pytest.raises(SkinportRateLimitError) as exc_info:
            client.items()
        assert exc_info.value.retry_after is None

    def test_empty_retry_after(self, client):
        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=429,
            headers={"Retry-After": ""},
            text="",
        )
        with pytest.raises(SkinportRateLimitError) as exc_info:
            client.items()
        assert exc_info.value.retry_after is None


# -- request logging -------------------------------------------------------


class TestRequestLogging:
    def test_request_logs_debug(self, client, caplog):
        import logging

        client._session = MagicMock()
        client._session.request.return_value = make_response(json_data=[])
        with caplog.at_level(logging.DEBUG, logger="skinport.client"):
            client.items()
        assert "Request: GET" in caplog.text
        assert "Response: 200" in caplog.text

    def test_error_response_logged(self, client, caplog):
        import logging

        client._session = MagicMock()
        client._session.request.return_value = make_response(
            status_code=500, text="Server Error"
        )
        with caplog.at_level(logging.DEBUG, logger="skinport.client"):
            with pytest.raises(SkinportAPIError):
                client.items()
        assert "Response: 500" in caplog.text


# -- pagination iterator ---------------------------------------------------


class TestTransactionsIter:
    def test_single_page(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            json_data={
                "data": [{"id": 1}, {"id": 2}],
                "pagination": {"page": 1, "pages": 1, "limit": 100, "order": "desc"},
            },
        )
        result = list(auth_client.account.transactions_iter())
        assert result == [{"id": 1}, {"id": 2}]
        assert auth_client._session.request.call_count == 1

    def test_multiple_pages(self, auth_client):
        page1 = make_response(
            json_data={
                "data": [{"id": 1}],
                "pagination": {"page": 1, "pages": 3, "limit": 1, "order": "desc"},
            },
        )
        page2 = make_response(
            json_data={
                "data": [{"id": 2}],
                "pagination": {"page": 2, "pages": 3, "limit": 1, "order": "desc"},
            },
        )
        page3 = make_response(
            json_data={
                "data": [{"id": 3}],
                "pagination": {"page": 3, "pages": 3, "limit": 1, "order": "desc"},
            },
        )
        auth_client._session = MagicMock()
        auth_client._session.request.side_effect = [page1, page2, page3]

        result = list(auth_client.account.transactions_iter(limit=1))

        assert result == [{"id": 1}, {"id": 2}, {"id": 3}]
        assert auth_client._session.request.call_count == 3

    def test_empty_data(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            json_data={
                "data": [],
                "pagination": {"page": 1, "pages": 1, "limit": 100, "order": "desc"},
            },
        )
        result = list(auth_client.account.transactions_iter())
        assert result == []

    def test_passes_order_param(self, auth_client):
        auth_client._session = MagicMock()
        auth_client._session.request.return_value = make_response(
            json_data={
                "data": [],
                "pagination": {"page": 1, "pages": 1, "limit": 100, "order": "asc"},
            },
        )
        list(auth_client.account.transactions_iter(order="asc"))
        params = auth_client._session.request.call_args[1]["params"]
        assert params["order"] == "asc"

    def test_is_lazy_iterator(self, auth_client):
        page1 = make_response(
            json_data={
                "data": [{"id": 1}],
                "pagination": {"page": 1, "pages": 2, "limit": 1, "order": "desc"},
            },
        )
        page2 = make_response(
            json_data={
                "data": [{"id": 2}],
                "pagination": {"page": 2, "pages": 2, "limit": 1, "order": "desc"},
            },
        )
        auth_client._session = MagicMock()
        auth_client._session.request.side_effect = [page1, page2]

        it = auth_client.account.transactions_iter(limit=1)
        # No request made yet until we consume
        assert auth_client._session.request.call_count == 0
        first = next(it)
        assert first == {"id": 1}
        assert auth_client._session.request.call_count == 1
