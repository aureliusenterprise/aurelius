import functools
import logging
import random
import time
from dataclasses import dataclass
from typing import Callable, Protocol, Tuple, Type, TypeVar, Union

T = TypeVar("T")

logger = logging.getLogger("retry")


class RetryError(Exception):
    """Exception raised when the maximum number of retries is exceeded."""

    def __init__(self, attempts: int, message: str = "Max retries exceeded") -> None:
        self.attempts = attempts
        super().__init__(f"{message}. Attempts: {attempts}")


class RetryStrategy(Protocol):
    """Protocol for defining retry strategies."""

    def sleep(self, attempts: int) -> None:
        """Sleep for a duration based on the retry strategy."""


@dataclass
class FixedDelay(RetryStrategy):
    """Simple retry strategy with a fixed delay."""

    delay: float = 1

    def __post_init__(self) -> None:
        if self.delay <= 0:
            message = "Delay must be greater than 0"
            raise ValueError(message)

    def sleep(self, attempts: int) -> None:  # noqa: ARG002
        """Sleep for a fixed duration."""
        time.sleep(self.delay)


@dataclass
class ExponentialBackoff(RetryStrategy):
    """Exponential backoff retry strategy."""

    initial_delay: float = 1
    multiplier: float = 1.5
    ceil: float = 60
    jitter: Tuple[float, float] = (0, 1)

    def __post_init__(self) -> None:
        if self.initial_delay <= 0:
            message = "Initial delay must be greater than 0"
            raise ValueError(message)
        if self.multiplier <= 1:
            message = "Multiplier must be greater than 1"
            raise ValueError(message)
        if self.ceil <= 0:
            message = "Ceil must be greater than 0"
            raise ValueError(message)
        if not (0 <= self.jitter[0] < self.jitter[1]):
            message = "Jitter must be a tuple with 0 <= min < max"
            raise ValueError(message)

    def sleep(self, attempts: int) -> None:
        """Sleep for a duration based on the exponential backoff strategy."""
        current_delay = functools.reduce(
            lambda x, _: x * self.multiplier + random.uniform(*self.jitter),  # noqa: S311
            range(attempts),
            self.initial_delay,
        )
        time.sleep(min(current_delay, self.ceil))


def retry(  # noqa: ANN201
    retry_strategy: RetryStrategy,
    catch: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    max_retries: int = 5,
):
    """
    Decorate a function to retry it upon exceptions, using a configurable retry strategy.

    This decorator allows for retrying a function call according to a specified retry strategy. It catches specified
    exceptions and retries the function call, delaying subsequent retries based on the strategy provided. After
    exceeding the maximum number of retries, reraises the last exception or raises a `RetryError`.

    The following retry strategies are available:

    - `FixedDelay`: A simple retry strategy with a fixed delay between retries.
    - `ExponentialBackoff`: A retry strategy with an exponentially increasing delay between retries.

    Parameters
    ----------
    retry_strategy : RetryStrategy
        The retry strategy to use, which must implement the `RetryStrategy` protocol.
    catch : type[Exception] | tuple[type[Exception], ...], optional
        A (tuple of) exception types that should be caught and retried. Defaults to catching all exceptions.
    max_retries : int, optional
        The maximum number of retries before giving up and raising a `RetryError`. Defaults to 5.

    Returns
    -------
    Callable[..., T]
        A wrapped version of the original function that incorporates retry logic.

    Raises
    ------
    RetryError
        If the function does not succeed within the maximum number of retries specified.

    Examples
    --------
    Using the `retry` decorator with a fixed delay strategy:

    >>> @retry(FixedDelay(delay=2), max_retries=3)
    ... def may_fail(num):
    ...     if num < 0.5:
    ...         raise ValueError("Number is too small")
    ...     return "Success"

    The `may_fail` function will be retried up to 3 times if a `ValueError` is raised, with a 2-second delay between
    retries.

    Using the `retry` decorator with an exponential backoff strategy:

    >>> @retry(ExponentialBackoff(initial_delay=1, multiplier=2), max_retries=5)
    ... def may_fail(num):
    ...     if num < 0.5:
    ...         raise ValueError("Number is too small")
    ...     return "Success"

    The `may_fail` function will be retried up to 5 times if a `ValueError` is raised, with an exponentially increasing
    delay between retries.

    Notes
    -----
    The retry decorator is useful in scenarios where operations are prone to transient failures, such as network
    requests or accessing external resources that may temporarily be unavailable.
    """

    def decorator(func: Callable[..., T]):  # noqa: ANN202
        @functools.wraps(func)
        def wrapper(*args: ..., **kwargs: ...) -> T:
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except catch:  # noqa: PERF203
                    attempts += 1
                    logger.warning("Attempt %d failed", attempts, exc_info=True)
                    if attempts == max_retries:
                        raise
                    retry_strategy.sleep(attempts)
            raise RetryError(attempts)

        return wrapper

    return decorator
