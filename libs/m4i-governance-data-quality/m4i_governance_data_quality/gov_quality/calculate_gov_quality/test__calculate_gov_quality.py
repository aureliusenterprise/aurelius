from m4i_atlas_core import (BusinessDataDomain, BusinessDataDomainAttributes,
                            ObjectId)
from pandas import Series
from pytest import fixture

from m4i_governance_data_quality.rules import get_rules_for_type
from .calculate_gov_quality import calculate_gov_quality


@fixture
def a():
    person_ref = ObjectId(
        type_name="m4i_person",
        guid="test"
    )

    attributes = BusinessDataDomainAttributes(
        qualified_name="test",
        name="test",
        definition="example",
        domain_lead=[person_ref],
        source=[]
    )

    relationship_attributes = {
        "dataEntity": [],
        "domainLead": [person_ref]
    }

    return BusinessDataDomain(
        guid="b",
        attributes=attributes,
        relationship_attributes=relationship_attributes
    )
# END a


@fixture
def b():
    attributes = BusinessDataDomainAttributes(
        qualified_name="test",
        name="test",
    )

    data_entity_ref = ObjectId(
        type_name="m4i_data_entity",
        guid="test"
    )

    relationship_attributes = {
        "dataEntity": [data_entity_ref],
        "domainLead": []
    }

    return BusinessDataDomain(
        guid="a",
        attributes=attributes,
        relationship_attributes=relationship_attributes
    )
# END b


def test__calculate_gov_quality_single(a: BusinessDataDomain):
    rules = get_rules_for_type('m4i_data_domain')
    results = calculate_gov_quality(a, rules=rules)

    print(a)

    assert all(results[a.guid] == Series([1, 1, 0, 1], index=results.index))
# END test__calculate_gov_quality_single


def test__calculate_gov_quality_multiple(a: BusinessDataDomain, b: BusinessDataDomain):
    rules = get_rules_for_type('m4i_data_domain')
    results = calculate_gov_quality(a, b, rules=rules)

    assert all(results[a.guid] == Series([1, 1, 0, 1], index=results.index))
    assert all(results[b.guid] == Series([1, 0, 1, 0], index=results.index))
# END test__calculate_gov_quality_multiple
