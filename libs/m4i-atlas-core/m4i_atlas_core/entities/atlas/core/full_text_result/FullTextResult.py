from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..entity_header import EntityHeader


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FullTextResult(DataClassJsonMixin):

    entity: EntityHeader
    score: int

# END FullTextResult
