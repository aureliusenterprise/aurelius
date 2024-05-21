from dataclasses import dataclass, field
from typing import Dict, List

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..entity_header import EntityHeader
from ..lineage_direction import LineageDirection
from ..lineage_relation import LineageRelation


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LineageInfoBase(DataClassJsonMixin):

    base_entity_guid: str
    lineage_depth: int
    lineage_direction: LineageDirection

# END LineageInfoBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LineageInfoDefaultsBase(DataClassJsonMixin):

    guid_entity_map: Dict[str, EntityHeader] = field(default_factory=dict)
    relations: List[LineageRelation] = field(default_factory=list)

# END LineageInfoDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LineageInfo(LineageInfoDefaultsBase, LineageInfoBase):

    pass

# END LineageInfo
