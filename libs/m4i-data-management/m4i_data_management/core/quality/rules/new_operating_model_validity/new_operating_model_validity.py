from pandas import DataFrame, Series

BASKETS = ['Project', 'BU direct', 'Generic', 'Fleet', 'Yard']


def new_operating_model_validity(data: DataFrame, basket_column: str, hierarchical_org: str, functional_org: str) -> Series:
    """
    Following the new operationg model, `hierarchical organisation` and `functional organisation` must be the same if `basket` is one of: 

    - Project
    - BU direct
    - Generic 
    - Fleet
    - Yard 

    If `hierarchical organisation` and `functional organisation` are the same, or if `basket` is none of the above, assign a score of 1.
    Otherwise, assign a score of 0.
    """

    def check(value):
        is_applicable_basket = value[basket_column] in BASKETS
        are_orgs_equal = value[hierarchical_org] == value[functional_org]
        return 1 if not is_applicable_basket or are_orgs_equal else 0
    # END check

    return data[[basket_column, hierarchical_org, functional_org]].apply(check, axis=1)
# END new_operating_model_validity
