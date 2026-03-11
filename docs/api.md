<a href="../skinport/client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
# <kbd>module</kbd> `skinport`

```python
import skinport

# Public endpoints (no credentials required)
client = skinport.Client()

# Authenticated endpoints
client = skinport.Client(
    client_id="<skinport_client_id>",
    client_secret="<skinport_client_secret>",
)
```

<a href="../skinport/client.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
## <kbd>class</kbd> `Client`

HTTP client for the Skinport REST API. Can be used as a context manager:

```python
with skinport.Client() as client:
    items = client.items()
```

**Constructor:**

```python
Client(*, client_id=None, client_secret=None, base_url=None, rate_limit=True, timeout=30)
```

 - <b>`client_id`</b>:<br>
   <i>string [optional]</i><br>
   API client ID (required for authenticated endpoints).
 - <b>`client_secret`</b>:<br>
   <i>string [optional]</i><br>
   API client secret (required for authenticated endpoints).
 - <b>`base_url`</b>:<br>
   <i>string [optional]</i><br>
   Override the default API base URL (`https://api.skinport.com/v1/`).
 - <b>`rate_limit`</b>:<br>
   <i>boolean [optional]</i><br>
   <i>Default `True`</i>.<br>
   Enable client-side sliding-window throttling (8 requests per 5 minutes per endpoint group). Set to `False` to disable.
 - <b>`timeout`</b>:<br>
   <i>float [optional]</i><br>
   <i>Default `30`</i>.<br>
   Request timeout in seconds. Set to `None` to disable.

<a href="../skinport/client.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
### <kbd>method</kbd> `items`

```python
items(*, app_id=730, currency="EUR", tradable=True)
```

Get all items listed for sale on the marketplace.

**Arguments:**

 - <b>`app_id`</b>:<br>
   <i>int [optional]</i><br>
   <i>Default `730`</i>.<br>
   The app_id for the inventory's game.
 - <b>`currency`</b>:<br>
   <i>string [optional]</i><br>
   <i>Default `EUR`</i>.<br>
   The currency for pricing.
   Supported: AUD, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP, HRK, NOK, PLN, RUB, SEK, TRY, USD.
 - <b>`tradable`</b>:<br>
   <i>boolean [optional]</i><br>
   <i>Default `True`</i>.<br>
   If true, show only tradable items on the marketplace.

**Returns:**
  A list of dicts with item pricing and metadata.

**Example:**

```python
client.items(app_id=730, currency="EUR", tradable=True)
[{'created_at': 1607718784,
  'currency': 'EUR',
  'item_page': 'https://skinport.com/item/1st-lieutenant-farlow-swat',
  'market_hash_name': '1st Lieutenant Farlow | SWAT',
  'market_page': 'https://skinport.com/market?item=1st%20Lieutenant%20Farlow&cat=Agent&type=SWAT',
  'max_price': 14.99,
  'mean_price': 5.21,
  'median_price': 4.50,
  'min_price': 1.33,
  'quantity': 16,
  'suggested_price': 1.33,
  'updated_at': 1644096927},
  ...
]
```

<a href="../skinport/client.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
### <kbd>method</kbd> `sales.history`

```python
client.sales.history(*, market_hash_name=None, app_id=730, currency="EUR")
```

Get aggregated sales data for items sold on Skinport. Provides statistics
across 24-hour, 7-day, 30-day, and 90-day windows including min, max, avg,
median prices and volume.

**Arguments:**

 - <b>`market_hash_name`</b>:<br>
   <i>string [optional]</i><br>
   The item's names, comma-delimited.
 - <b>`app_id`</b>:<br>
   <i>int [optional]</i><br>
   <i>Default `730`</i>.<br>
   The app_id for the inventory's game.
 - <b>`currency`</b>:<br>
   <i>string [optional]</i><br>
   <i>Default `EUR`</i>.<br>
   The currency for pricing.
   Supported: AUD, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP, HRK, NOK, PLN, RUB, SEK, TRY, USD.

**Returns:**
  A list of dicts with sales statistics per item.

**Example:**

```python
client.sales.history(market_hash_name="Glove Case Key")
[{'currency': 'EUR',
  'item_page': 'https://skinport.com/item/glove-case-key',
  'market_hash_name': 'Glove Case Key',
  'market_page': 'https://skinport.com/market?item=Glove%20Case%20Key&cat=Key',
  'last_24_hours': {'avg': 8.27, 'max': 8.27, 'min': 8.27, 'median': 8.27, 'volume': 1},
  'last_7_days': {'avg': 8.27, 'max': 8.27, 'min': 8.27, 'median': 8.27, 'volume': 4},
  'last_30_days': {'avg': 7.58, 'max': 8.27, 'min': 6.9, 'median': 7.49, 'volume': 14},
  'last_90_days': {'avg': 6.61, 'max': 8.27, 'min': 5.32, 'median': 6.50, 'volume': 49}}
]
```

<a href="../skinport/client.py#L137"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
### <kbd>method</kbd> `sales.out_of_stock`

```python
client.sales.out_of_stock(*, app_id=730, currency="EUR")
```

Get information about items currently out of stock on the marketplace.

**Arguments:**

 - <b>`app_id`</b>:<br>
   <i>int [optional]</i><br>
   <i>Default `730`</i>.<br>
   The app_id for the inventory's game.
 - <b>`currency`</b>:<br>
   <i>string [optional]</i><br>
   <i>Default `EUR`</i>.<br>
   The currency for pricing.
   Supported: AUD, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP, HRK, NOK, PLN, RUB, SEK, TRY, USD.

**Returns:**
  A list of dicts with out-of-stock item data.

**Example:**

```python
client.sales.out_of_stock(app_id=730, currency="EUR")
[{'avg_sale_price': 7738.98,
  'currency': 'EUR',
  'market_hash_name': '★ M9 Bayonet | Doppler (Factory New)',
  'sales_last_90d': 4,
  'suggested_price': 9913.6,
  'version': 'Sapphire'},
  ...
]
```

<a href="../skinport/client.py#L149"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
### <kbd>method</kbd> `account.transactions`

```python
client.account.transactions(*, page=1, limit=100, order="desc")
```

Get a paginated list of account transactions. **Requires authentication.**

**Arguments:**

 - <b>`page`</b>:<br>
   <i>int [optional]</i><br>
   <i>Default `1`</i>.<br>
   Pagination page number.
 - <b>`limit`</b>:<br>
   <i>int [optional]</i><br>
   <i>Default `100`</i>.<br>
   Limit results between 1 and 100.
 - <b>`order`</b>:<br>
   <i>string [optional]</i><br>
   <i>Default `desc`</i>.<br>
   Order results by asc or desc.

**Returns:**
  A dict with `data` (transaction list) and `pagination` keys.

**Example:**

```python
client.account.transactions(page=1, limit=3, order="asc")
{'data': [{'amount': 345.86,
           'created_at': '2021-10-28T12:21:02.536Z',
           'currency': 'EUR',
           'fee': None,
           'id': 5706008,
           'items': [{'buyer_country': 'LU',
                      'market_hash_name': '★ StatTrak™ Survival Knife | Fade '
                                          '(Factory New)',
                      'sale_id': 4809936,
                      'seller_country': 'NL'}],
           'status': 'complete',
           'sub_type': None,
           'type': 'purchase',
           'updated_at': '2021-10-28T12:21:28.331Z'}],
 'pagination': {'limit': 3, 'order': 'asc', 'page': 1, 'pages': 7}}
```

### <kbd>method</kbd> `account.transactions_iter`

```python
client.account.transactions_iter(*, limit=100, order="desc")
```

Iterate over all account transactions, handling pagination automatically.
Yields individual transaction dicts. **Requires authentication.**

**Arguments:**

 - <b>`limit`</b>:<br>
   <i>int [optional]</i><br>
   <i>Default `100`</i>.<br>
   Results per page, 1--100.
 - <b>`order`</b>:<br>
   <i>string [optional]</i><br>
   <i>Default `desc`</i>.<br>
   Order results by asc or desc.

**Returns:**
  An iterator of transaction dicts.

**Example:**

```python
for txn in client.account.transactions_iter():
    print(txn["id"], txn["type"], txn["amount"])
```

---

<a href="../skinport/salefeed.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
## <kbd>class</kbd> `SaleFeed`

Live sale feed from the Skinport marketplace via WebSocket (Socket.IO).

```python
from skinport import SaleFeed

feed = SaleFeed(app_id=730, currency="EUR", locale="en")

@feed.on_event
def handle(data):
    print(data["eventType"], data["sales"])

feed.connect()  # blocks until disconnected
```

**Constructor:**

```python
SaleFeed(*, app_id=730, currency="EUR", locale="en", base_url="https://skinport.com", reconnect=True, reconnect_delay=5)
```

 - <b>`app_id`</b>:<br>
   <i>int [optional]</i><br>
   <i>Default `730`</i>.<br>
   The app_id for the inventory's game.
 - <b>`currency`</b>:<br>
   <i>string [optional]</i><br>
   <i>Default `EUR`</i>.<br>
   The currency for pricing.
 - <b>`locale`</b>:<br>
   <i>string [optional]</i><br>
   <i>Default `en`</i>.<br>
   Result language. Supported: en, de, ru, fr, zh, nl, fi, es, tr.
 - <b>`base_url`</b>:<br>
   <i>string [optional]</i><br>
   Override the default Socket.IO endpoint URL (`https://skinport.com`).
 - <b>`reconnect`</b>:<br>
   <i>boolean [optional]</i><br>
   <i>Default `True`</i>.<br>
   Automatically reconnect on unexpected disconnection.
 - <b>`reconnect_delay`</b>:<br>
   <i>float [optional]</i><br>
   <i>Default `5`</i>.<br>
   Seconds to wait before reconnecting.

### <kbd>method</kbd> `on_event`

Register a callback for sale feed events. Can be used as a decorator.
The callback receives a dict with `eventType` (`"listed"` or `"sold"`)
and `sales` (list of item dicts).

If a callback raises an exception, it is logged and the remaining callbacks
still fire.

### <kbd>method</kbd> `connect`

```python
connect(*, background=False)
```

Connect to the sale feed and start receiving events.

 - <b>`background`</b>:<br>
   <i>boolean [optional]</i><br>
   <i>Default `False`</i>.<br>
   If True, connect in the background and return immediately.

### <kbd>method</kbd> `on_disconnect`

Register a callback for disconnection events. Can be used as a decorator.
The callback receives no arguments.

If a callback raises an exception, it is logged and the remaining callbacks
still fire.

### <kbd>method</kbd> `disconnect`

Disconnect from the sale feed. Suppresses auto-reconnect.

### <kbd>property</kbd> `connected`

Whether the feed is currently connected.

---

## Exceptions

All exceptions inherit from `SkinportError`:

 - **`SkinportError`** — base exception for all library errors.
 - **`SkinportAPIError`** — raised on non-200 API responses. Has `status_code` and `message` attributes.
 - **`SkinportAuthError`** — raised on 401/403 responses or missing credentials.
 - **`SkinportRateLimitError`** — raised on 429 responses. Has `retry_after` attribute (float or None).
