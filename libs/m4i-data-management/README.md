# M4I Data Management

This library contains all core functionality around data management for Models4Insight.

## Installation

Please ensure your `Python` environment is on version `3.7`. Some dependencies do not work with any later versions of `Python`.

To install `m4i-data-management` and all required dependencies to your active `Python` environment, please run the following command from the project root folder:

```
pip install -e .
```

To install `m4i-data-management` including development dependencies, please run the following command instead:

```
pip install -e .[dev]
```

Please make a copy of `config.sample.py` and `credentials.sample.py` and rename the files to `config.py` and `credentials.py` respectively.

The `config.py` and `credentials.py` files should be located in the root folder of the project, or otherwise on the `PYTHON_PATH`.

Please remember to set the configuration parameters you want to use.

## Testing

This project uses `pytest` as its unit testing framework.
To run the unit tests, please install `pytest` and then execute the `pytest` command from the project root folder.

Unit tests are grouped per module.
Unit test modules are located in the same folder as their respective covered modules.
They can be recognized by the `test__` module name prefix, followed by the name of the covered module.

## Contacts

| Name              | Role                | Email                               |
| ----------------- | ------------------- | -----------------------------       |
| Thijs Franck      | Lead developer      | thijs.franck@aureliusenterprise.com |
