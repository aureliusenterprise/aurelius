from dataclasses import dataclass, field
from typing import List, Union

from dataclasses_json import DataClassJsonMixin, dataclass_json


@dataclass_json
@dataclass
class AppSearchDocument(DataClassJsonMixin):
    """Represents a document in the App Search index."""

    guid: str
    name: str
    referenceablequalifiedname: str
    typename: str

    # Elasticsearch document ID
    id: Union[str, None] = None

    # Data quality related attributes
    dqscore_accuracy: float = field(default_factory=float)
    dqscore_timeliness: float = field(default_factory=float)
    dqscoresum_accuracy: float = field(default_factory=float)
    dqscore_validity: float = field(default_factory=float)
    dqscore_completeness: float = field(default_factory=float)
    dqscoresum_validity: float = field(default_factory=float)
    dqscorecnt_overall: float = field(default_factory=float)
    dqscorecnt_timeliness: float = field(default_factory=float)
    dqscoresum_timeliness: float = field(default_factory=float)
    dqscoresum_completeness: float = field(default_factory=float)
    dqscore_uniqueness: float = field(default_factory=float)
    dqscorecnt_completeness: float = field(default_factory=float)
    dqscoresum_uniqueness: float = field(default_factory=float)
    dqscore_overall: float = field(default_factory=float)
    dqscorecnt_uniqueness: float = field(default_factory=float)
    businessruleid: float = field(default_factory=float)
    dqscoresum_overall: float = field(default_factory=float)
    dqscorecnt_accuracy: float = field(default_factory=float)
    dqscorecnt_validity: float = field(default_factory=float)

    # Entity details
    parentguid: Union[str, None] = None
    entityname: Union[str, None] = None
    definition: Union[str, None] = None
    email: Union[str, None] = None
    deriveddataownerguid: Union[str, None] = None
    deriveddomainleadguid: Union[str, None] = None
    deriveddatastewardguid: Union[str, None] = None
    sourcetype: Union[str, None] = None

    # Relationships
    derivedfield: List[str] = field(default_factory=list)
    deriveddataattribute: List[str] = field(default_factory=list)
    deriveddataentity: List[str] = field(default_factory=list)
    qualityguid_completeness: List[str] = field(default_factory=list)
    deriveddataentityguid: List[str] = field(default_factory=list)
    derivedsystem: List[str] = field(default_factory=list)
    qualityguid_timeliness: List[str] = field(default_factory=list)
    deriveddataset: List[str] = field(default_factory=list)
    derivedsystemguid: List[str] = field(default_factory=list)
    breadcrumbname: List[str] = field(default_factory=list)
    breadcrumbguid: List[str] = field(default_factory=list)
    deriveddataattributeguid: List[str] = field(default_factory=list)
    deriveddatasetnames: List[str] = field(default_factory=list)
    derivedperson: List[str] = field(default_factory=list)
    derivedfieldguid: List[str] = field(default_factory=list)
    derivedentityguids: List[str] = field(default_factory=list)
    deriveddatasetguids: List[str] = field(default_factory=list)
    deriveddatasetguid: List[str] = field(default_factory=list)
    derivedprocess: List[str] = field(default_factory=list)
    derivedprocessguid: List[str] = field(default_factory=list)
    classificationstext: List[str] = field(default_factory=list)
    qualityguid_uniqueness: List[str] = field(default_factory=list)
    derivedpersonguid: List[str] = field(default_factory=list)
    qualityguid_accuracy: List[str] = field(default_factory=list)
    derivedcollection: List[str] = field(default_factory=list)
    deriveddatadomainguid: List[str] = field(default_factory=list)
    derivedcollectionguid: List[str] = field(default_factory=list)
    qualityguid_validity: List[str] = field(default_factory=list)
    deriveddatadomain: List[str] = field(default_factory=list)
    derivedentitynames: List[str] = field(default_factory=list)
    breadcrumbtype: List[str] = field(default_factory=list)
    supertypenames: List[str] = field(default_factory=list)
