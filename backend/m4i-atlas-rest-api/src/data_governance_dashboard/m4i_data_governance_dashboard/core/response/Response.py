from dataclasses import dataclass, field
from typing import Dict

from dataclasses_json.api import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Response:
    """
    Response Class : Final result structure
    """
    total_number_of_domains: int
    total_number_of_active_domains: int
    domains: Dict[str, dict] = field(default_factory=dict)
