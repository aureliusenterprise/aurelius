from dataclasses import dataclass, field

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
    id: str | None = None

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
    parentguid: str | None = None
    entityname: str | None = None
    definition: str | None = None
    email: str | None = None
    deriveddataownerguid: str | None = None
    deriveddomainleadguid: str | None = None
    deriveddatastewardguid: str | None = None

    # Relationships
    derivedfield: list[str] = field(default_factory=list)
    deriveddataattribute: list[str] = field(default_factory=list)
    deriveddataentity: list[str] = field(default_factory=list)
    qualityguid_completeness: list[str] = field(default_factory=list)
    deriveddataentityguid: list[str] = field(default_factory=list)
    derivedsystem: list[str] = field(default_factory=list)
    qualityguid_timeliness: list[str] = field(default_factory=list)
    deriveddataset: list[str] = field(default_factory=list)
    derivedsystemguid: list[str] = field(default_factory=list)
    breadcrumbname: list[str] = field(default_factory=list)
    breadcrumbguid: list[str] = field(default_factory=list)
    deriveddataattributeguid: list[str] = field(default_factory=list)
    deriveddatasetnames: list[str] = field(default_factory=list)
    derivedperson: list[str] = field(default_factory=list)
    derivedfieldguid: list[str] = field(default_factory=list)
    derivedentityguids: list[str] = field(default_factory=list)
    deriveddatasetguids: list[str] = field(default_factory=list)
    deriveddatasetguid: list[str] = field(default_factory=list)
    derivedprocess: list[str] = field(default_factory=list)
    derivedprocessguid: list[str] = field(default_factory=list)
    classificationstext: list[str] = field(default_factory=list)
    qualityguid_uniqueness: list[str] = field(default_factory=list)
    derivedpersonguid: list[str] = field(default_factory=list)
    qualityguid_accuracy: list[str] = field(default_factory=list)
    derivedcollection: list[str] = field(default_factory=list)
    deriveddatadomainguid: list[str] = field(default_factory=list)
    derivedcollectionguid: list[str] = field(default_factory=list)
    qualityguid_validity: list[str] = field(default_factory=list)
    deriveddatadomain: list[str] = field(default_factory=list)
    derivedentitynames: list[str] = field(default_factory=list)
    breadcrumbtype: list[str] = field(default_factory=list)
    supertypenames: list[str] = field(default_factory=list)
