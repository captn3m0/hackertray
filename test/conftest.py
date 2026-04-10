"""Block all network access during tests.

Any urllib.request.urlopen call that isn't mocked will raise immediately
instead of hitting the network.
"""

import urllib.request

import pytest


def _blocked_urlopen(*args, **kwargs):
    raise RuntimeError(
        f"Network access not allowed in tests (urlopen called with {args!r})"
    )


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", _blocked_urlopen)
