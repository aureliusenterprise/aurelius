from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GovQualityRuleDefinition(DataClassJsonMixin):
    active: bool
    compliant_message: str
    expression: str
    expression_version: int
    id: int
    noncompliant_message: str
    qualified_name: str
    quality_dimension: str
    rule_description: str
    rule_title: str
    type: str
    guid: str
# END GovQualityRuleDefinition
