# ConfigStore

`ConfigStore` is a powerful, singleton-based configuration store providing an easy-to-use interface to store, retrieve, and manage configuration settings.

- [ConfigStore](#configstore)
  - [Features](#features)
  - [How to use](#how-to-use)
    - [Initializing the ConfigStore](#initializing-the-configstore)
    - [Storing Configuration Settings](#storing-configuration-settings)
    - [Retrieving Configuration Settings](#retrieving-configuration-settings)
    - [Resetting the ConfigStore](#resetting-the-configstore)
    - [Error Handling](#error-handling)

## Features

- Singleton-based implementation ensures a single source of truth for your configuration settings.
- Ability to load your configuration settings on application start.
- Easy storage and retrieval of configuration settings using simple `get` and `set` methods.
- Support for default values and required settings.
- Bulk retrieval and storage of settings using `get_many` and `set_many` methods.

## How to use

Please find examples of how to use the `ConfigStore` below.

### Initializing the ConfigStore

To start using the `ConfigStore`, first import the necessary components and initialize the singleton instance:

```python
from config import config
from credentials import credentials

from m4i_atlas_core import ConfigStore

store = ConfigStore.get_instance()
store.load({
   **config,
   **credentials
})
```

In this example, the `config.py` and `credentials.py` files are imported to obtain the necessary configuration parameters and credentials. The `ConfigStore` is then initialized using the `get_instance()` method, and the configuration and credential dictionaries are merged and loaded into the `ConfigStore` using the `load()` method.

> **Note**: It is recommended to initialize the ConfigStore once when the application starts.

### Storing Configuration Settings

To store a configuration setting, use the `set` method:

```python
store.set("key", "value")
```

To store multiple configuration settings at once, use the set_many method:

```python
store.set_many(key1="value1", key2="value2", key3="value3")
```

### Retrieving Configuration Settings

To retrieve a configuration setting, use the `get` method. If the key is not present in the `ConfigStore`, it returns `None` by default.

```python
value = store.get("key")
```

You can also provide a default value if the key is not found:

```python
value = store.get("key", default="default_value")
```

If a key is required and not found in the `ConfigStore`, you can raise a `MissingRequiredConfigException` by setting the required parameter to `True`:

```python
value = store.get("key", required=True)
```

To retrieve multiple configuration settings at once, use the `get_many` method:

```python
key1, key2, key3 = store.get_many("key1", "key2", "key3")
```

You can also provide default values and required flags for the keys:

```python
defaults = {"key1": "default_value1", "key2": "default_value2"}
required = {"key1": True, "key2": False}

key1, key2, key3 = store.get_many("key1", "key2", "key3", defaults=defaults, required=required)
```

If all keys are required, you can use the `all_required` parameter as a shorthand:

```python
key1, key2, key3 = store.get_many("key1", "key2", "key3", all_required=True)
```

### Resetting the ConfigStore

To reset the `ConfigStore` and remove all stored configuration settings, use the reset method:

```python
store.reset()
```

This will clear the `ConfigStore` and reset it to an empty state.

### Error Handling

The `ConfigStore` raises a `MissingRequiredConfigException` when a required key is not found and no default value has been provided. This exception can be caught and handled as needed in your application:

```python
from m4i_atlas_core import MissingRequiredConfigException

try:
    value = store.get("key", required=True)
except MissingRequiredConfigException as ex:
    # Handle the case of a missing configuration
```
