# Changelog

All notable changes to this project will be documented in this file.

This file format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).\
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-11

### New
- Full library rewrite with modern architecture.
- `Client` class with namespace-based API: `client.sales.history()`,
  `client.sales.out_of_stock()`, `client.account.transactions()`.
- `base_url` parameter on `Client` and `SaleFeed` for custom endpoints.
- `rate_limit` parameter on `Client` — client-side sliding-window throttling
  (enabled by default, 8 requests per 5 minutes per endpoint group).
- `timeout` parameter on `Client` (default 30s) to prevent hanging requests.
- `account.transactions_iter()` — pagination iterator that yields all
  transactions across pages automatically.
- `SaleFeed` class for real-time WebSocket sale events via Socket.IO.
- `SaleFeed` callback error handling — a failing callback is logged and does
  not prevent remaining callbacks from firing.
- `SaleFeed.on_disconnect` callback for disconnection events.
- `SaleFeed` auto-reconnect on unexpected disconnection (`reconnect=True`
  by default, configurable delay via `reconnect_delay`).
- Request/response logging at DEBUG level via `logging.getLogger("skinport.client")`.
- Custom exception hierarchy: `SkinportError`, `SkinportAPIError`,
  `SkinportAuthError`, `SkinportRateLimitError`.
- `py.typed` marker for PEP 561 type-checking support.
- Comprehensive test suite (150+ unit tests, 12 integration tests).
- CI workflow: pytest matrix across Python 3.10–3.14.

### Changes
- Migrated from `setup.py` to `pyproject.toml`.
- Updated GitHub Actions (`checkout`, `setup-python`) from v2 to v4.
- README: install-from-source command updated to `pip install -e .`.
- README: added rate limiting documentation section.

### Removed
- Removed legacy `skinport/core.py` module.
- Removed `setup.py` (replaced by `pyproject.toml`).

## [0.1.2] - 2022-02-08

### Fixes
- fix return in `_request()`

## [0.1.1] - 2022-02-08

### New
- improved documentation ([see](./docs/api.md))
- added User-Agent header, append module version
- fetch module version from `setup.py` and create version attribute

### Changes
- `token` property is intended for internal use

## [0.1.0] - 2022-01-27

Initial release.
