# aurelius-sdk

Shared Python utility library for Aurelius services: logging, cloud helpers,
Postgres change-data-capture, event broadcasting, and test infrastructure.

Part of the template **spine**.

## Optional extras

The base package depends only on `httpx`. Everything else is an extra, and each
submodule raises a clear error at import time if its extra is missing:

| Extra        | Enables                                |
| ------------ | -------------------------------------- |
| `logging`    | `logger.py` (colored console logging)  |
| `postgresql` | `postgresql/` (CDC listener, tsquery)  |
| `aws`        | `aws.py` (Secrets Manager)             |
| `azure`      | `msal.py` (Azure AD / MSAL tokens)     |
| `testing`    | `testing.py` (testcontainers fixtures) |
| `full`       | All of the above                       |

```bash
uv add "aurelius-sdk[postgresql]"   # example: depend on one extra
```

## Modules

- `logger.py` — `setup_logger()`: consistent colored logging across services
- `events.py` — `Broadcaster[T]`: fan-out async event distribution (used by the
  FastAPI example's SSE pipeline)
- `postgresql/` — `PostgresListener` (async `LISTEN`/`NOTIFY`) and
  `sanitize_tsquery()` for safe full-text search
- `encoding.py` — zig-zag integer encoding helpers
- `aws.py` — `get_secret()` for AWS Secrets Manager
- `msal.py` — MSAL-based token acquisition for Azure services
- `testing.py` — shared testcontainers-based fixtures

> [!NOTE]
> The package root is intentionally empty — always import from submodules, e.g.
> `from aurelius_sdk.logger import setup_logger`.

## Testing

```bash
uv run pytest libs/python/aurelius-sdk/tests
```
