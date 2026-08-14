# Base Class Extraction Pattern

Use when 2+ classes share identical infrastructure code (authentication, HTTP sessions, retries, config loading).

## Target Structure

```
BEFORE: client_a.py (300 lines, 60 duplicated)
        client_b.py (400 lines, 60 duplicated)
        client_c.py (500 lines, 60 duplicated — being retired)

AFTER:  base.py     (120 lines — shared infrastructure)
        client_a.py (240 lines — inherits base)
        client_b.py (340 lines — inherits base)
        client_c.py (16 lines — backward-compat shim if being retired)
```

## Base Class Design

```python
# base.py
class ServiceBase:
    """Shared infrastructure for all Service API clients."""

    BASE_URL = "https://api.example.com/v1"

    def __init__(self, api_key=None, timeout=30, max_retries=3):
        self.api_key = api_key or os.environ.get("SERVICE_API_KEY")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("API key required")

        # Session with retries
        self.session = requests.Session()
        retry = Retry(total=max_retries, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def _request(self, method, endpoint, json=None) -> dict:
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.request(method=method, url=url, headers=self._headers(), json=json, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> bool:
        raise NotImplementedError("Subclasses must implement health_check")
```

## Subclass Pattern

```python
# client_a.py
class ClientA(ServiceBase):
    def __init__(self, api_key=None, timeout=30, max_retries=3):
        super().__init__(api_key=api_key, timeout=timeout, max_retries=max_retries)
        self._cache = None  # Subclass-specific state

    def get_items(self):
        return self._request("GET", "items")

    def health_check(self) -> bool:
        try:
            self.get_items()
            return True
        except Exception:
            return False
```

## Critical: Preserve Timeout Defaults

If subclasses had different default timeouts, keep them in the subclass signature:

```python
# Base: timeout=30 (general default)
class ServiceBase:
    def __init__(self, timeout=30, ...): ...

# Subclass A: timeout=30 (same as base — fine)
class ClientA(ServiceBase):
    def __init__(self, timeout=30, ...): super().__init__(timeout=timeout, ...)

# Subclass B: timeout=60 (different! — MUST keep in subclass signature)
class ClientB(ServiceBase):
    def __init__(self, timeout=60, ...): super().__init__(timeout=timeout, ...)
```

If you remove the timeout from ClientB's signature, it silently inherits 30s from the base — a regression.

## Backward-Compat Shim

When retiring an old combined class in favor of specialized subclasses:

```python
# old_client.py (was 500 lines, now a 4-line shim)
"""Backward-compatibility shim. Use ClientA or ClientB directly."""
from .client_a import ClientA as OldClient, create_client_a as create_old_client
```

This preserves `from module.old_client import OldClient` for any code that hasn't migrated yet.

## What to Extract vs. What to Keep

**Extract to base:**
- Authentication / credential loading
- HTTP session setup with retries
- Common request helper (`_request`, `_headers`)
- Shared configuration (base URL, timeouts)

**Keep in subclasses:**
- Domain-specific methods (get_items, create_report, etc.)
- Subclass-specific caches or state
- Custom health checks
- Default values that differ from the base

## Common Mistakes

- **Extracting too much** — if only 2 of 3 subclasses need a method, it doesn't belong in the base
- **Losing timeout defaults** — always check each subclass's `__init__` signature before and after
- **Breaking the shim** — the old class name must resolve to a class with the same methods the callers used. If the old class had methods from multiple subclasses, the shim must point to whichever subclass has the methods callers actually use.
