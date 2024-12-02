from dataclasses import dataclass, field
from typing import List

from dataclasses_json import DataClassJsonMixin, dataclass_json


@dataclass_json
@dataclass
class GovDataQualityDocument(DataClassJsonMixin):
    """Represents a document in the Governance Data Quality index."""

    id: str
    guid: str
    name: str
    qualifiedname: str
    qualityqualifiedname: str
    dataqualityruletypename: str
    dataqualitytype: str
    dataqualityruledescription: str
    dataqualityruledimension: str
    result_id: str
    business_rule_id: str
    entity_guid: str
    expression: str
    compliant: float
    usedattributes: List[str] = field(default_factory=list)
