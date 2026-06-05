from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json

from ..struct_def import StructDef


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class BusinessMetadataDef(StructDef):
    pass


# END BusinessMetadataDef
