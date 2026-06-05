import pytest
from pandas import DataFrame

from .producer import Producer


def get_new() -> DataFrame:
    return DataFrame({"id": [1], "abc": ["def"], "ghi": ["jkl"]}).set_index("id")  # type: ignore[return-value]


# END get_new


def get_old() -> DataFrame:
    return DataFrame({"id": [1], "abc": ["def"], "ghi": ["mno"]}).set_index("id")  # type: ignore[return-value]


# END get_old


def transform(data: DataFrame):
    data["abc"] = "test"
    return data


# END transform


def propagate(data: DataFrame):
    pass


# END _propagate


@pytest.fixture
def producer():
    return Producer(get_new=get_new, get_old=get_old, propagate=propagate)  # type: ignore[arg-type]


# END producer


@pytest.fixture
def producer_transform():
    return Producer(
        get_new=get_new,
        get_old=get_old,
        transform=transform,
        propagate=propagate,  # type: ignore[arg-type]
    )


# END producer_transform
