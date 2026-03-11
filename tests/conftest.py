import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from skinport import Client


def _load_env() -> None:
    """Load variables from ~/.env if present (for integration tests)."""
    env_file = Path.home() / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ[key.strip()] = value.strip().strip('"')


_load_env()


@pytest.fixture
def client():
    """Anonymous client (no credentials, rate limiting off for tests)."""
    return Client(rate_limit=False)


@pytest.fixture
def auth_client():
    """Authenticated client with test credentials (rate limiting off for tests)."""
    return Client(client_id="test_id", client_secret="test_secret", rate_limit=False)


def make_response(status_code=200, json_data=None, headers=None, text=""):
    """Build a mock :class:`requests.Response`."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.text = text
    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = ValueError("No JSON")
    return resp
