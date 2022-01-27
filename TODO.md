# skinport TODO

## Command line interface

skinport should provide a basic commandline interface named `skinport` to let
you query all available API endpoints.

### Example

```bash
$ skinport account transactions --page=1 --limit=1 --order=asc
```

## Split classes into dedicated files

At the time of writing this (Jan. 2022), the SkinPort API is comprised of a
relatively low number of endpoints. Once the amount of endpoints grow, keeping
track of them in a single file (`core.py`) won't be an easy task.

To improve readability and feature-proof the library, look into splitting
classes into their own separate file.

### Example

```
skinport/
├── LICENSE
├── README.md
├── setup.py
├── skinport
│   ├── account.py    -> contains 'Account' class and all related endpoints
│   ├── base.py       -> contains main 'SkinPort' class and HTTP related functions
│   ├── sales.py      -> contains 'Sales' class and all related endpoints
│   └── __init__.py
└── TODO.md

```


