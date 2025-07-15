# aurelius-kafka

This library provides common utilities for working with Apache Kafka.

## Installation

You can include `aurelius-kafka` in your project by adding it to your `pyproject.toml`:

```toml
[tool.poetry.dependencies.aurelius-kafka]
develop = true
path = "../../libs/aurelius-kafka"
```

Ensure the path points to the correct location of the `aurelius-kafka` library.

### Extras

The `aurelius-kafka` library includes optional dependencies that can be installed based on your needs:

| Extra Name | Description                                                                 |
| ---------- | --------------------------------------------------------------------------- |
| `msk`      | Includes dependencies for Amazon MSK (Managed Streaming for Kafka) support. |

You can install these extras by specifying them in your `pyproject.toml`:

```toml
[tool.poetry.dependencies.aurelius-kafka]
develop = true
extras = ["msk"]
path = "../../libs/aurelius-kafka"
```

## Documentation

::: aurelius_kafka

::: aurelius_kafka.msk
