from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LineageRelationBase(DataClassJsonMixin):

    from_entity_id: str
    relationship_id: str
    to_entity_id: str

# END LineageRelationBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LineageRelationDefaultsBase(DataClassJsonMixin):

    pass

# END LineageRelationDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LineageRelation(LineageRelationDefaultsBase, LineageRelationBase):

    pass

# END LineageRelation
