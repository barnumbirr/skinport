# -*- coding: utf-8 -*-

import json
import base64
import requests
from requests_toolbelt.utils import dump

class SkinPort:

    def __init__(self):
        from . import API_BASE_URL, API_VERSION
        self.api_base_url = API_BASE_URL
        self.api_base_url += f"{API_VERSION}/"

    @property
    def token(self):
        from . import CLIENT_ID, CLIENT_SECRET
        return base64.b64encode(
            f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")
        ).decode("utf-8")

    def _request(self, method, path, params=None, payload=None):
        params = params or {}

        response = requests.request(
            method,
            self.api_base_url + path,
            params=params,
            data=json.dumps(payload) if payload else payload,
            headers={
                # "User-Agent": f"skinport/{__version__} - github.com/barnumbirr/skinport",
                "Content-Type": "application/json",
                "Authorization": f"Basic {self.token}"},
        )

        # print(dump.dump_all(response).decode("utf-8"))
        response.encoding = "utf-8"
        return response.json()

    def _get(self, path, params=None):
        """ Read API resources. """
        return self._request('GET', path, params=params)

    def _post(self, path, params=None, payload=None):
        """ Create new API resources. """
        return self._request('POST', path, params=params, payload=payload)

    def _put(self, path, params=None, payload=None):
        """ Modify existing API resources. """
        return self._request('PUT', path, params=params, payload=payload)

    def _delete(self, path, params=None, payload=None):
        """ Remove API resources. """
        return self._request('DELETE', path, params=params, payload=payload)

    def items(self, **kwargs):
        """
        Get all in stock items listed for sale.

        Arguments:
            app_id: int
                [optional] The app_id for the inventory's game (default 730).
            currency: string
                [optional] The currency for pricing. Default EUR.
                Supported: AUD, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP, HRK,
                NOK, PLN, RUB, SEK, TRY, USD.

        Returns:
            A dict representation of the JSON returned by the API.
        """
        return self._get("items", kwargs)

    class Sales:

        @staticmethod
        def history(**kwargs):
            """
            Get sales history for specified item.

            Arguments:
                market_hash_name: string
                    [required] The item's names, comma-delimited.
                app_id: int
                    [optional] The app_id for the inventory's game
                    (default 730).
                currency: string
                    [optional] The currency for pricing. Default EUR.
                    Supported: AUD, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP, HRK,
                    NOK, PLN, RUB, SEK, TRY, USD.

            Returns:
                A dict representation of the JSON returned by the API.
            """
            return SkinPort()._get("sales/history", kwargs)

        @staticmethod
        def out_of_stock(**kwargs):
            """
            Get sales history for out-of-stock items.

            Arguments:
                app_id: int
                    [optional] The app_id for the inventory's game
                    (default 730).
                currency: string
                    [optional] The currency for pricing. Default EUR.
                    Supported: AUD, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP, HRK,
                    NOK, PLN, RUB, SEK, TRY, USD.

            Returns:
                A dict representation of the JSON returned by the API.
            """
            return SkinPort()._get("sales/out-of-stock", kwargs)

    class Account:

        @staticmethod
        def transactions(**kwargs):
            """
            Get all available items listed for sale.

            Arguments:
                page: int
                    [optional] Pagination Page (default 1).
                limit: int
                    [optional] Limit results between 1 and 100 (default 100).
                order: string
                    [optional] Order results by asc or desc (default desc).

            Returns:
                A dict representation of the JSON returned by the API.
            """
            return SkinPort()._get("account/transactions", kwargs)
