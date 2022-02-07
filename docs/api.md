<a href="../skinport/core.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
# <kbd>module</kbd> `skinport`

```python
import skinport

skinport.CLIENT_ID = "<skinport_client_id>"
skinport.CLIENT_SECRET = "<skinport_client_id>"

skins = skinport.SkinPort()
```

<a href="../skinport/core.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
## <kbd>class</kbd> `SkinPort`

<a href="../skinport/core.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
### <kbd>method</kbd> `items`

```python
items(**kwargs)
```

Get all in stock items listed for sale.

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
 - <b>tradable</b>:<br>
   <i>boolean [optional]</i><br>
   <i>Default `false`</i>.<br>
   If true, it shows only tradable items on the market.

**Returns:**
  A dict representation of the JSON returned by the API.

**Example:**

```python
skins.items(app_id=730, currency="EUR", tradable=false)
[{'created_at': 1607718784,
  'currency': 'EUR',
  'item_page': 'https://skinport.com/item/1st-lieutenant-farlow-swat',
  'market_hash_name': '1st Lieutenant Farlow | SWAT',
  'market_page': 'https://skinport.com/market?item=1st%20Lieutenant%20Farlow&cat=Agent&type=SWAT',
  'max_price': 14.99,
  'mean_price': 5.21,
  'min_price': 1.33,
  'quantity': 16,
  'suggested_price': 1.33,
  'updated_at': 1644096927},
 {'created_at': 1612431333,
  'currency': 'EUR',
  'item_page': 'https://skinport.com/item/2020-rmr-challengers',
  'market_hash_name': '2020 RMR Challengers',
  'market_page': 'https://skinport.com/market?item=2020%20RMR%20Challengers&cat=Container',
  'max_price': 5,
  'mean_price': 0.91,
  'min_price': 0.11,
  'quantity': 424,
  'suggested_price': 0.13,
  'updated_at': 1644096927},
  ...
]
```

<a href="../skinport/core.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
## <kbd>class (nested)</kbd> `Sales`

<a href=".../skinport/core.py#L79"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
### <kbd>staticmethod</kbd> `history`

```python
history(**kwargs)
```

Get sales history for specified item.

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
 - <b>market_hash_name</b>:<br>
   <i>string [required]</i><br>
   The item's names, comma-delimited.

**Returns:**
  A dict representation of the JSON returned by the API.

**Example:**

```python
skins.Sales.history(app_id=730, currency="EUR", market_hash_name="Glove Case Key,★ Karambit | Slaughter (Minimal Wear)")
[{'currency': 'EUR',
  'item_page': 'https://skinport.com/item/glove-case-key',
  'last_30_days': {'avg': 7.58, 'max': 8.27, 'min': 6.9, 'volume': 14},
  'last_7_days': {'avg': 8.27, 'max': 8.27, 'min': 8.27, 'volume': 4},
  'last_90_days': {'avg': 6.61, 'max': 8.27, 'min': 5.32, 'volume': 49},
  'market_hash_name': 'Glove Case Key',
  'market_page': 'https://skinport.com/market?item=Glove%20Case%20Key&cat=Key',
  'sales': [{'price': 8.27, 'sold_at': 1643907869, 'wear_value': None},
            {'price': 8.27, 'sold_at': 1643907869, 'wear_value': None},
            {'price': 8.27, 'sold_at': 1643817928, 'wear_value': None},
            {'price': 8.27, 'sold_at': 1643603329, 'wear_value': None},
            {'price': 8.27, 'sold_at': 1643545474, 'wear_value': None},
            {'price': 7.49, 'sold_at': 1643434729, 'wear_value': None},
            {'price': 7.19, 'sold_at': 1643355680, 'wear_value': None},
            {'price': 7.49, 'sold_at': 1643186037, 'wear_value': None},
            {'price': 7.15, 'sold_at': 1643141829, 'wear_value': None},
            {'price': 7.15, 'sold_at': 1642906340, 'wear_value': None}]},
 {'currency': 'EUR',
  'item_page': 'https://skinport.com/item/karambit-slaughter-minimal-wear',
  'last_30_days': {'avg': 485.83, 'max': 500, 'min': 449.73, 'volume': 12},
  'last_7_days': {'avg': 464.96, 'max': 480.18, 'min': 449.73, 'volume': 2},
  'last_90_days': {'avg': 465.66, 'max': 500, 'min': 420.43, 'volume': 28},
  'market_hash_name': '★ Karambit | Slaughter (Minimal Wear)',
  'market_page': 'https://skinport.com/market?item=Slaughter&cat=Knife&type=Karambit',
  'sales': [{'price': 480.18,
             'sold_at': 1643743302,
             'wear_value': 0.0775609090924263},
            {'price': 449.73,
             'sold_at': 1643698970,
             'wear_value': 0.10993880778551102},
            {'price': 499.89,
             'sold_at': 1643189867,
             'wear_value': 0.0842127650976181},
            {'price': 479.22,
             'sold_at': 1642864867,
             'wear_value': 0.08626371622085571},
            {'price': 498.89,
             'sold_at': 1642863993,
             'wear_value': 0.12153729051351547},
            {'price': 479,
             'sold_at': 1642846422,
             'wear_value': 0.13493385910987854},
            {'price': 493.08,
             'sold_at': 1642698178,
             'wear_value': 0.07426711171865463},
            {'price': 478.93,
             'sold_at': 1642410194,
             'wear_value': 0.11009060591459274},
            {'price': 500,
             'sold_at': 1642367510,
             'wear_value': 0.13694848120212555},
            {'price': 497.98,
             'sold_at': 1642301975,
             'wear_value': 0.11055292189121246}]}
]
```

<a href="../skinport/core.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
### <kbd>staticmethod</kbd> `out_of_stock`

```python
out_of_stock(**kwargs)
```

Get sales history for out-of-stock items.

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
  A dict representation of the JSON returned by the API.

**Example:**

```python
skins.Sales.out_of_stock(app_id=730, currency="EUR")
[{'avg_sale_price': 7738.98,
  'currency': 'EUR',
  'market_hash_name': '★ M9 Bayonet | Doppler (Factory New)',
  'sales_last_90d': 4,
  'suggested_price': 9913.6,
  'version': 'Sapphire'},
 {'avg_sale_price': 22484.59,
  'currency': 'EUR',
  'market_hash_name': '★ Sport Gloves | Vice (Factory New)',
  'sales_last_90d': 1,
  'suggested_price': 22288.61,
  'version': None},
  ...
]
```

<a href="../skinport/core.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
## <kbd>class (nested)</kbd> `Account`

<a href="../skinport/core.py#L121"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>
### <kbd>staticmethod</kbd> `transactions`

```python
transactions(**kwargs)
```

Get all available items listed for sale.

**Arguments:**

 - <b>`page`</b>:<br>
   <i>int [optional]</i><br>
   <i>Default `1`</i>.<br>
   Pagination Page.
 - <b>`limit`</b>:<br>
   <i>int [optional]</i><br>
   <i>Default `100`</i>.<br>
   Limit results between 1 and 100.
 - <b>order</b>:<br>
   <i>string [optional]</i><br>
   <i>Default `desc`</i>.<br>
   Order results by asc or desc.

**Returns:**
  A dict representation of the JSON returned by the API.

**Example:**

```python
skins.Account.transactions(page=1, limit=3, order="asc")
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
           'updated_at': '2021-10-28T12:21:28.331Z'},
          {'amount': 0.04,
           'created_at': '2021-11-20T13:47:13.371Z',
           'currency': 'EUR',
           'fee': 0.01,
           'id': 6040560,
           'items': [{'buyer_country': 'PL',
                      'market_hash_name': 'R8 Revolver | Desert Brush (Minimal '
                                          'Wear)',
                      'sale_id': 5095281,
                      'seller_country': 'LU'}],
           'status': 'complete',
           'sub_type': 'item',
           'type': 'credit',
           'updated_at': '2021-11-20T13:47:13.371Z'},
          {'amount': 0.05,
           'created_at': '2021-11-23T15:37:12.848Z',
           'currency': 'EUR',
           'fee': 0.01,
           'id': 6088892,
           'items': [{'buyer_country': 'PL',
                      'market_hash_name': 'Sawed-Off | Parched (Minimal Wear)',
                      'sale_id': 5095282,
                      'seller_country': 'LU'}],
           'status': 'complete',
           'sub_type': 'item',
           'type': 'credit',
           'updated_at': '2021-11-23T15:37:12.848Z'}],
 'pagination': {'limit': 3, 'order': 'asc', 'page': 1, 'pages': 7}}
```
