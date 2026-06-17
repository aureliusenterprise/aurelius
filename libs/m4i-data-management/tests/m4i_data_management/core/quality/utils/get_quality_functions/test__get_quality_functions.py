from inspect import getmembers, isfunction
from typing import List

import pytest

from m4i_data_management.core.quality import rules
from m4i_data_management.core.quality.utils.get_quality_functions.get_quality_functions import (
    get_quality_functions,
)


@pytest.fixture
def members() -> List:
    return getmembers(rules, isfunction)


# END members


def test__get_quality_functions_includes_all_quality_rules(members: List):
    quality_functions = get_quality_functions()

    for name, _ in members:
        assert name in quality_functions
    # END LOOP


# END test__get_quality_functions_includes_all_quality_rules
