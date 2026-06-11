from dataclasses import dataclass, field
from typing import Dict

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class ConstraintDefBase(DataClassJsonMixin):
    type: str


# END ConstraintDefBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class ConstraintDefDefaultsBase(DataClassJsonMixin):
    params: Dict[str, dict] = field(default_factory=dict)


# END ConstraintDefDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class ConstraintDef(ConstraintDefDefaultsBase, ConstraintDefBase):
    pass


# END ConstraintDef
