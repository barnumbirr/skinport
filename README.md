# skinport

A Python wrapper around the [Skinport API](https://skinport.com/). To learn
more about Skinport API, check out the
[official documentation](https://docs.skinport.com/#introduction).

## Installation

*skinport* is available on PyPI:

```bash
$ pip install skinport
```

To install from source use:

```bash
$ python setup.py install
```

## Usage

```python
import skinport

skinport.CLIENT_ID = "<skinport_client_id>"
skinport.CLIENT_SECRET = "<skinport_client_id>"
skins = skinport.SkinPort()

print(skins.items())
```

## Skinport API Key

You will need an API key to Skinport to access the API. To obtain a key, follow
these steps:

1) Register for and verify an [account](https://skinport.com/signup).
2) [Log into](https://skinport.com/account) your account.
3) Scroll down to the Skinport API section.
4) Click on `Generate API key` and follow the instructions.


## License

```
Copyright 2022 Martin Simon

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
