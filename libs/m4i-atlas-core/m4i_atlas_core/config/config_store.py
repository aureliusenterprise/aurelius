from logging import warning
from typing import Any, Dict, Iterator, Optional, TypeVar

T = TypeVar('T')

_instance: 'ConfigStore' = None


class MissingRequiredConfigException(Exception):
    """
    Exception raised when a required configuration setting is missing and no default value has been specified.
    """
# END MissingRequiredConfigException


class ConfigStore:
    """
    A singleton class for storing and retrieving configuration values.
    """

    _config: Dict[str, Any] = {}

    @classmethod
    def get_instance(cls) -> 'ConfigStore':
        """
        Returns the singleton instance of the ConfigStore class.

        Returns:
            The singleton instance of the ConfigStore class.
        """

        global _instance

        if not _instance:
            _instance = cls()
        # END IF

        return _instance
    # END get_instance

    @classmethod
    def initialize(cls, config: Dict[str, Any]) -> 'ConfigStore':
        """
        Initializes the singleton instance of the ConfigStore class with the given config dictionary.

        Args:
            config: The configuration dictionary to load into the ConfigStore.

        Returns:
            The initialized singleton instance of the ConfigStore class.
        """

        if not _instance:
            instance = cls.get_instance()
            instance.load(config)
        # END IF

        return _instance
    # END initialize

    def get(self, key: str, default: Optional[T] = None, required: bool = False) -> T:
        """
        Returns the value of the configuration setting with the given key.

        If the key is not found, returns the given default value, if specified. If required is `True` and no default value
        is specified, raises a MissingRequiredConfigException.

        Args:
            key: The key of the configuration value to retrieve.
            default: The default value to return if the key is not found. Defaults to None.
            required: Whether the key is required. If `True` and no default value is specified, raises a
                MissingRequiredConfigException. Defaults to `False`.

        Returns:
            The value of the configuration setting with the given key.

        Raises:
            MissingRequiredConfigException: If the key is required and no default value is specified.
        """

        if key not in self._config:
            if required and default is None:
                raise MissingRequiredConfigException(
                    f"No value has been configured for required key {{{key}}}. Please provide a value for this key in the configuration or specify a default value."
                )
            else:
                warning(
                    f"No value has been configured for key {{{key}}}. Returning the default value instead."
                )
            # END IF
        # END IF

        return self._config.get(key, default)
    # END get

    def get_many(self, *keys: str, defaults: Dict[str, T] = None, required: Dict[str, bool] = None,
                 all_required: bool = False) -> Iterator[T]:
        """
        Returns an iterator over the values of the configuration settings with the given keys.

        If a default value is specified in the defaults dictionary for a key that is not found, that default value is
        used. If a required value is `True` for a key that is not found and no default value is specified, raises a
        MissingRequiredConfigException. If all_required is `True`, raises a MissingRequiredConfigException if any of the
        specified keys are missing.

        Args:
            *keys: The keys of the configuration values to retrieve.
            defaults: A dictionary of default values to use if a key is not found. Defaults to an empty dictionary.
            required: A dictionary of flags indicating whether a key is required. If a key is required and no default
                value is specified, raises a MissingRequiredConfigException. Defaults to an empty dictionary.
            all_required: Whether all of the specified keys are required. If `True` and any of the specified keys are missing,
            raises a MissingRequiredConfigException. Defaults to `False`.

        Returns:
            An iterator over the values of the configuration settings with the given keys.

        Raises:
            MissingRequiredConfigException: If a required key is missing and no default value is specified, or if
                all_required is `True` and any of the specified keys are missing.
        """

        if defaults is None:
            defaults = {}
        # END IF

        if required is None:
            required = {}
        # END IF

        def resolver(key):
            return self.get(key, defaults.get(key), all_required or required.get(key))
        # END resolver

        return map(resolver, keys)
    # END get_many

    def load(self, config: Dict[str, Any]) -> None:
        """
        Loads the configuration settings from the given config dictionary.

        Args:
            config: The configuration dictionary to load into the ConfigStore.
        """

        self.set_many(**config)
    # END load

    def reset(self) -> None:
        """
        Resets the configuration settings to an empty dictionary.
        """
        self._config = {}
    # END reset

    def set(self, key: str, value: Any) -> None:
        """
        Sets the value of the configuration setting with the given key.

        Args:
            key: The key of the configuration value to set.
            value: The value to set the configuration value to.
        """

        self._config[key] = value
    # END set

    def set_many(self, **kwargs) -> None:
        """
        Sets the values of the configuration settings specified as keyword arguments.

        Args:
            **kwargs: The configuration key/value pairs to set.
        """

        for key, value in kwargs.items():
            self.set(key, value)
        # END LOOP
    # END set_many
# END ConfigStore
