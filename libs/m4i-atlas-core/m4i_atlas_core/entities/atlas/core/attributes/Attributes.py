from dataclasses import dataclass, field

from dataclasses_json import (CatchAll, DataClassJsonMixin, LetterCase,
                              Undefined, dataclass_json)


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.INCLUDE)
@dataclass
class Attributes(DataClassJsonMixin):

    # Catches all attributes that are not specifically defined as a regular dictionary
    unmapped_attributes: CatchAll = field(default_factory=dict)  # name change from API due to attributes in schema

# END Attributes
