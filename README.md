# skinport

An unofficial Python wrapper around the [Skinport](https://skinport.com/) API.

## Installation

*skinport* is available on PyPI:

```bash
$ pip install skinport
```

To install from source use:

```bash
$ pip install -e .
```

## Usage

```python
import skinport

# Public endpoints work without credentials
client = skinport.Client()
items = client.items(app_id=730, currency="EUR")
client.sales.history(market_hash_name="AK-47 | Redline (Field-Tested)")
client.sales.out_of_stock()

# Authenticated endpoints require credentials
client = skinport.Client(
    client_id="<skinport_client_id>",
    client_secret="<skinport_client_secret>",
)
transactions = client.account.transactions()
```

The client can also be used as a context manager:

```python
with skinport.Client() as client:
    items = client.items()
    history = client.sales.history(market_hash_name="AK-47 | Redline (Field-Tested)")
```

### Rate Limiting

Client-side rate limiting is enabled by default (8 requests per 5 minutes per
endpoint group), matching the Skinport API limits. The client will automatically
sleep when the limit is reached. To disable:

```python
client = skinport.Client(rate_limit=False)
```

### WebSocket Sale Feed

```python
from skinport import SaleFeed

feed = SaleFeed(app_id=730, currency="EUR", locale="en")

@feed.on_event
def handle(data):
    print(data["eventType"], data["sales"])

feed.connect()  # blocks until disconnected
```

## Documentation

Documentation for the skinport library is available [here](./docs/api.md).\
To learn more about the Skinport API, check out the
[official documentation](https://docs.skinport.com/).

## Skinport API Key

You will need an API key to Skinport to access authenticated endpoints. To
obtain a key, follow these steps:

1) Register for and verify an [account](https://skinport.com/signup).
2) [Log into](https://skinport.com/account) your account.
3) Scroll down to the Skinport API section.
4) Click on `Generate API key` and follow the instructions.


## License

```
Copyright 2022-2026 Martin Simon

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

```

## Buy me a coffee?

If you feel like buying me a coffee (or a beer?), donations are welcome:

```
BTC : bc1qq04jnuqqavpccfptmddqjkg7cuspy3new4sxq9
DOGE: DRBkryyau5CMxpBzVmrBAjK6dVdMZSBsuS
ETH : 0x2238A11856428b72E80D70Be8666729497059d95
LTC : MQwXsBrArLRHQzwQZAjJPNrxGS1uNDDKX6
```
