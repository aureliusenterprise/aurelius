# aurelius-sdk

This library provides common utilities for Aurelius projects.

## Installation

You can include `aurelius-sdk` in your project by adding it to your `pyproject.toml`:

```toml
[tool.poetry.dependencies.aurelius-sdk]
develop = true
path = "../../libs/aurelius-sdk"
```

Ensure the path points to the correct location of the `aurelius-sdk` library.

### Extras

The `aurelius-sdk` library includes optional dependencies that can be installed based on your needs:

| Extra Name | Description                                                    |
| ---------- | -------------------------------------------------------------- |
| `logger`   | Includes dependencies for logging utilities.                   |
| `msal`     | Includes dependencies for Microsoft Identity Platform support. |

You can install these extras by specifying them in your `pyproject.toml`:

```toml
[tool.poetry.dependencies.aurelius-sdk]
develop = true
extras = ["logger", "msal"]
path = "../../libs/aurelius-sdk"
```

## Documentation

::: aurelius_sdk.logger

::: aurelius_sdk.msal
