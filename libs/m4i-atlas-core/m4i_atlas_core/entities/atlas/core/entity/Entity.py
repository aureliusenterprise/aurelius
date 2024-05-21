from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Union

from dataclasses_json import LetterCase, dataclass_json

from ..attributes import Attributes
from ..classification import Classification
from ..exceptions import TypesDefNotFoundException
from ..object_id import ObjectId
from ..status import Status
from ..struct import Struct, StructBase, StructDefaultsBase
from ..term_assignment_header import TermAssignmentHeader
from ..utils import create_placehoder_guid


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntityBase(StructBase):

    pass

# END EntityBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntityDefaultsBase(StructDefaultsBase):

    classifications: List[Classification] = field(default_factory=list)
    classification_names: List[str] = field(default_factory=list)
    create_time: Optional[float] = None
    created_by: Optional[str] = None
    custom_attributes: Optional[Attributes] = None
    display_text: Optional[str] = None
    guid: str = field(default_factory=create_placehoder_guid)
    home_id: Optional[str] = None
    is_incomplete: Optional[bool] = None
    labels: List[str] = field(default_factory=list)
    meanings: List[TermAssignmentHeader] = field(default_factory=list)
    provenance_type: Optional[int] = None
    proxy: Optional[bool] = None
    relationship_attributes: Optional[Dict[str, List[ObjectId]]] = None
    status: Optional[Status] = None
    update_time: Optional[float] = None
    updated_by: Optional[str] = None
    version: Optional[int] = None


# END EntityDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Entity(Struct, EntityDefaultsBase, EntityBase):

    @classmethod
    def get_type_def(cls):
        raise TypesDefNotFoundException(f'{cls.__name__}: Type Definition Not Found')

    def get_children(self) -> Iterable[ObjectId]:
        """
        Returns all children of this `Entity`.
        Intended to be overridden by subtypes that declare specific reference points.
        """
        return []
    # END get_children

    def get_parents(self) -> Iterable[ObjectId]:
        """
        Returns all parents of this `Entity`.
        Intended to be overridden by subtypes that declare specific reference points.
        """
        return []
    # END get_parents

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns all entity references made by this `Entity`
        Intended to be overridden by subtypes that declare specific reference points
        """
        return []
    # END get_referred_entities

# END Entity
