"""HTTP client for the Skinport REST API."""

from __future__ import annotations

import base64
import logging
import threading
import time
from collections import deque
from collections.abc import Iterator
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import requests

from .exceptions import (
    SkinportAPIError,
    SkinportAuthError,
    SkinportRateLimitError,
)

logger = logging.getLogger(__name__)

try:
    __version__ = version("skinport")
except PackageNotFoundError:
    __version__ = "dev"

_BASE_URL = "https://api.skinport.com/v1/"

_ERROR_MAP = {
    401: SkinportAuthError,
    403: SkinportAuthError,
    429: SkinportRateLimitError,
}

_RATE_LIMIT_REQUESTS = 8
_RATE_LIMIT_WINDOW = 300.0  # seconds (5 minutes)


class _RateLimiter:
    """Sliding-window rate limiter that tracks requests per endpoint group.

    Before each request, checks whether the window is full and sleeps
    the minimum time needed to stay within the limit.
    """

    __slots__ = ("_max_requests", "_window", "_history", "_lock")

    def __init__(self, max_requests: int, window: float) -> None:
        self._max_requests = max_requests
        self._window = window
        self._history: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def acquire(self, group: str) -> None:
        """Block until a request slot is available for *group*."""
        with self._lock:
            timestamps = self._history.get(group)
            if timestamps is None:
                timestamps = deque()
                self._history[group] = timestamps

            now = time.monotonic()
            while timestamps and timestamps[0] <= now - self._window:
                timestamps.popleft()

            if len(timestamps) >= self._max_requests:
                sleep_for = timestamps[0] + self._window - now
                if sleep_for > 0:
                    time.sleep(sleep_for)
                now = time.monotonic()
                while timestamps and timestamps[0] <= now - self._window:
                    timestamps.popleft()

            timestamps.append(time.monotonic())


class _Sales:
    """Namespace for sales-related endpoints.  Bound to a
    :class:`Client` instance via ``client.sales``."""

    __slots__ = ("_request",)

    def __init__(self, client: Client) -> None:
        self._request = client._request

    def history(
        self,
        *,
        market_hash_name: str | None = None,
        app_id: int = 730,
        currency: str = "EUR",
    ) -> list[dict[str, Any]]:
        """Get aggregated sales data for items sold on Skinport.

        Provides statistics across 24-hour, 7-day, 30-day, and 90-day
        windows including min, max, avg, median prices and volume.

        :param market_hash_name: item name(s), comma-delimited.
        :param app_id: game app ID (default ``730`` for CS2).
        :param currency: pricing currency code (default ``EUR``).
        :return: list of dicts with sales statistics per item.
        """
        params: dict[str, Any] = {"app_id": app_id, "currency": currency}
        if market_hash_name is not None:
            params["market_hash_name"] = market_hash_name
        return self._request("GET", "sales/history", params=params)

    def out_of_stock(
        self,
        *,
        app_id: int = 730,
        currency: str = "EUR",
    ) -> list[dict[str, Any]]:
        """Get information about items currently out of stock.

        :param app_id: game app ID (default ``730`` for CS2).
        :param currency: pricing currency code (default ``EUR``).
        :return: list of dicts with out-of-stock item data.
        """
        return self._request(
            "GET",
            "sales/out-of-stock",
            params={
                "app_id": app_id,
                "currency": currency,
            },
        )


class _Account:
    """Namespace for account-related endpoints.  Bound to a
    :class:`Client` instance via ``client.account``."""

    __slots__ = ("_request",)

    def __init__(self, client: Client) -> None:
        self._request = client._request

    def transactions(
        self,
        *,
        page: int = 1,
        limit: int = 100,
        order: str = "desc",
    ) -> dict[str, Any]:
        """Get a paginated list of account transactions.

        Requires authentication (*client_id* and *client_secret*).

        :param page: page number (default ``1``).
        :param limit: results per page, 1--100 (default ``100``).
        :param order: ``'asc'`` or ``'desc'`` (default ``'desc'``).
        :return: dict with ``'data'`` (transaction list) and
            ``'pagination'`` keys.
        """
        return self._request(
            "GET",
            "account/transactions",
            params={
                "page": page,
                "limit": limit,
                "order": order,
            },
            auth=True,
        )

    def transactions_iter(
        self,
        *,
        limit: int = 100,
        order: str = "desc",
    ) -> Iterator[dict[str, Any]]:
        """Iterate over all account transactions, handling pagination.

        Yields individual transaction dicts. Automatically fetches
        subsequent pages until all results are returned.

        Requires authentication (*client_id* and *client_secret*).

        :param limit: results per page, 1--100 (default ``100``).
        :param order: ``'asc'`` or ``'desc'`` (default ``'desc'``).
        :return: iterator of transaction dicts.
        """
        page = 1
        while True:
            result = self.transactions(page=page, limit=limit, order=order)
            yield from result["data"]
            pagination = result["pagination"]
            if page >= pagination["pages"]:
                break
            page += 1


class Client:
    """HTTP client for the Skinport REST API.

    Public endpoints (:meth:`items`, :attr:`sales`) work without
    credentials.  Authenticated endpoints (:attr:`account`) require
    *client_id* and *client_secret*.

    Can be used as a context manager to ensure the underlying session
    is closed::

        with skinport.Client() as client:
            items = client.items()

    :param client_id: API client ID (required for authenticated endpoints).
    :param client_secret: API client secret.
    :param base_url: override the default API base URL.
    :param rate_limit: enable client-side throttling to stay within API
        rate limits (default ``True``).  Set to ``False`` to disable.
    :param timeout: request timeout in seconds (default ``30``).
        Set to ``None`` to disable.
    """

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        base_url: str | None = None,
        rate_limit: bool = True,
        timeout: float | None = 30,
    ) -> None:
        self.base_url = base_url or _BASE_URL
        self.timeout = timeout
        self._client_id = client_id
        self._client_secret = client_secret
        self._limiter: _RateLimiter | None = (
            _RateLimiter(_RATE_LIMIT_REQUESTS, _RATE_LIMIT_WINDOW)
            if rate_limit
            else None
        )
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": (
                    f"skinport/{__version__} (github.com/barnumbirr/skinport)"
                ),
                "Accept-Encoding": "gzip, deflate, br",
            }
        )
        self.sales = _Sales(self)
        self.account = _Account(self)

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def __repr__(self) -> str:
        auth = "authenticated" if self._client_id else "anonymous"
        return f"<skinport.Client [{auth}]>"

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    # -- internal helpers --------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        if self._client_id is None or self._client_secret is None:
            raise SkinportAuthError(
                401,
                "client_id and client_secret are required for this endpoint",
            )
        token = base64.b64encode(
            f"{self._client_id}:{self._client_secret}".encode()
        ).decode()
        return {"Authorization": f"Basic {token}"}

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        auth: bool = False,
    ) -> Any:
        if self._limiter is not None:
            group = path.split("/")[0]
            self._limiter.acquire(group)

        headers = self._auth_headers() if auth else {}
        url = self.base_url + path

        logger.debug("Request: %s %s params=%s", method, url, params)

        resp = self._session.request(
            method,
            url,
            params=params or {},
            headers=headers,
            timeout=self.timeout,
        )

        logger.debug("Response: %s %s", resp.status_code, url)

        if resp.status_code != 200:
            exc_class = _ERROR_MAP.get(resp.status_code, SkinportAPIError)

            if exc_class is SkinportRateLimitError:
                retry_after = resp.headers.get("Retry-After")
                parsed_retry: float | None = None
                if retry_after:
                    try:
                        parsed_retry = float(retry_after)
                    except (ValueError, OverflowError):
                        logger.warning(
                            "Invalid Retry-After header: %r", retry_after
                        )
                raise SkinportRateLimitError(retry_after=parsed_retry)

            message = None
            try:
                body = resp.json()
                message = body.get("message") or body.get("error")
                if not message:
                    errors = body.get("errors")
                    if errors and isinstance(errors, list):
                        message = errors[0].get("message")
            except (ValueError, KeyError, AttributeError):
                message = resp.text or None

            raise exc_class(resp.status_code, message)

        try:
            return resp.json()
        except ValueError:
            raise SkinportAPIError(
                resp.status_code,
                "API returned invalid JSON",
            ) from None

    # -- public endpoints --------------------------------------------------

    def items(
        self,
        *,
        app_id: int = 730,
        currency: str = "EUR",
        tradable: bool = True,
    ) -> list[dict[str, Any]]:
        """Get all items listed for sale on the marketplace.

        :param app_id: game app ID (default ``730`` for CS2).
        :param currency: pricing currency code (default ``EUR``).
            Supported: AUD, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP,
            HRK, NOK, PLN, RUB, SEK, TRY, USD.
        :param tradable: if true, show only tradable items (default
            ``True``).
        :return: list of item dicts with pricing and metadata.
        """
        return self._request(
            "GET",
            "items",
            params={
                "app_id": app_id,
                "currency": currency,
                "tradable": "true" if tradable else "false",
            },
        )
