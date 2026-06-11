from m4i_governance_data_quality.rules.get_rules_for_type.get_rules_for_type import get_rules_for_type


def test__get_rules_for_type():
    rules = get_rules_for_type("m4i_data_domain")
    assert rules


# END test__get_rules_for_type
