"""Integration tests against the live Skinport API.

Run with::

    pytest -m integration

Requires ``SKINPORT_CLIENT_ID`` and ``SKINPORT_CLIENT_SECRET`` environment
variables (or entries in ``~/.env``).

API responses are cached per module to stay within rate limits
(8 requests per 5 minutes for items and sales/history).
"""

import os

import pytest

from skinport import Client
from skinport.exceptions import SkinportAuthError

pytestmark = pytest.mark.integration


# -- fixtures (module-scoped to minimize API calls) ------------------------


@pytest.fixture(scope="module")
def live_anon_client():
    """Anonymous client for public endpoints."""
    with Client() as c:
        yield c


@pytest.fixture(scope="module")
def live_client():
    """Authenticated client for account endpoints."""
    client_id = os.environ.get("SKINPORT_CLIENT_ID")
    client_secret = os.environ.get("SKINPORT_CLIENT_SECRET")
    if not client_id or not client_secret:
        pytest.skip("SKINPORT_CLIENT_ID and SKINPORT_CLIENT_SECRET required")
    with Client(client_id=client_id, client_secret=client_secret) as c:
        yield c


@pytest.fixture(scope="module")
def items_eur(live_anon_client):
    """Cached /v1/items response (EUR)."""
    return live_anon_client.items(app_id=730, currency="EUR")


@pytest.fixture(scope="module")
def items_usd(live_anon_client):
    """Cached /v1/items response (USD)."""
    return live_anon_client.items(app_id=730, currency="USD")


@pytest.fixture(scope="module")
def sales_history_response(live_anon_client):
    """Cached /v1/sales/history response for known items."""
    return live_anon_client.sales.history(
        market_hash_name="AK-47 | Redline (Field-Tested),Glove Case Key",
    )


@pytest.fixture(scope="module")
def out_of_stock_response(live_anon_client):
    """Cached /v1/sales/out-of-stock response."""
    return live_anon_client.sales.out_of_stock(app_id=730, currency="EUR")


# -- Items -----------------------------------------------------------------


class TestItemsLive:
    def test_returns_non_empty_list(self, items_eur):
        assert isinstance(items_eur, list)
        assert len(items_eur) > 0

    def test_item_has_expected_keys(self, items_eur):
        item = items_eur[0]
        expected = {
            "market_hash_name",
            "currency",
            "suggested_price",
            "item_page",
            "market_page",
            "min_price",
            "max_price",
            "mean_price",
            "median_price",
            "quantity",
            "created_at",
            "updated_at",
        }
        assert expected.issubset(item.keys())

    def test_currency_matches_request(self, items_eur, items_usd):
        assert items_eur[0]["currency"] == "EUR"
        assert items_usd[0]["currency"] == "USD"

    def test_quantity_is_non_negative(self, items_eur):
        for item in items_eur[:10]:
            assert item["quantity"] >= 0


# -- Sales history ---------------------------------------------------------


class TestSalesHistoryLive:
    def test_returns_non_empty_list(self, sales_history_response):
        assert isinstance(sales_history_response, list)
        assert len(sales_history_response) > 0

    def test_response_has_time_period_stats(self, sales_history_response):
        item = sales_history_response[0]
        assert "market_hash_name" in item
        assert "currency" in item
        for period in ("last_24_hours", "last_7_days", "last_30_days", "last_90_days"):
            assert period in item, f"missing {period}"
            stats = item[period]
            for key in ("min", "max", "avg", "median", "volume"):
                assert key in stats, f"missing {key} in {period}"

    def test_multiple_items_returned(self, sales_history_response):
        names = {item["market_hash_name"] for item in sales_history_response}
        assert "AK-47 | Redline (Field-Tested)" in names
        assert "Glove Case Key" in names


# -- Sales out of stock ----------------------------------------------------


class TestSalesOutOfStockLive:
    def test_returns_non_empty_list(self, out_of_stock_response):
        assert isinstance(out_of_stock_response, list)
        assert len(out_of_stock_response) > 0

    def test_item_has_expected_keys(self, out_of_stock_response):
        item = out_of_stock_response[0]
        expected = {
            "market_hash_name",
            "currency",
            "suggested_price",
            "avg_sale_price",
            "sales_last_90d",
        }
        assert expected.issubset(item.keys())


# -- Account transactions -------------------------------------------------


class TestAccountTransactionsLive:
    def test_returns_paginated_response(self, live_client):
        result = live_client.account.transactions(limit=1)
        assert "data" in result
        assert "pagination" in result
        assert isinstance(result["data"], list)
        pagination = result["pagination"]
        for key in ("page", "pages", "limit", "order"):
            assert key in pagination

    def test_pagination_params_respected(self, live_client):
        result = live_client.account.transactions(page=1, limit=2, order="asc")
        assert result["pagination"]["limit"] == 2
        assert result["pagination"]["order"] == "asc"

    def test_anonymous_client_raises_auth_error(self, live_anon_client):
        with pytest.raises(SkinportAuthError):
            live_anon_client.account.transactions()
