from dataclasses import dataclass

from dataclasses_json.api import LetterCase, dataclass_json


# Defined for understanding the Response model
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Details:
    """
    Details for each Program
    """
    name: int
    guid: str
    is_active: bool
    total_number_of_entities: int = 0
