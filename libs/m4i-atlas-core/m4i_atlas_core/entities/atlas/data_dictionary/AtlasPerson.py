from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Attributes, Entity, EntityBase, EntityDef,
                    EntityDefaultsBase, ObjectId, TypeCategory)
from ..m4i.M4IAttributes import M4IAttributesBase

atlas_person_attributes_def = [
    AttributeDef(
        name="email",
        type_name="string",
        is_unique=True,
        description="The email address of the actor in the organization",
        display_name="Email"
    ),
    AttributeDef(
        name="name",
        type_name="string",
        description="The name of the actor in the organization",
        display_name="Name"
    )
]
atlas_person_super_type = ["m4i_referenceable"]

atlas_person_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_person",
    description="Represents a specific actor in the organization",
    type_version="1.0",
    attribute_defs=atlas_person_attributes_def,
    super_types=atlas_person_super_type
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AtlasPersonAttributesBase(M4IAttributesBase):
    pass
# END AtlasPersonAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AtlasPersonAttributesDefaultsBase(Attributes):
    name: Optional[str] = None
    email: Optional[str] = None
    source: List[ObjectId] = field(default_factory=list)
# END AtlasPersonAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AtlasPersonAttributes(AtlasPersonAttributesDefaultsBase, AtlasPersonAttributesBase):
    pass
# END AtlasPersonAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AtlasPersonBase(EntityBase):
    attributes: AtlasPersonAttributes
# ENDAtlasPersonBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AtlasPersonDefaultsBase(EntityDefaultsBase):
    pass
# END AtlasPersonDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AtlasPerson(AtlasPersonDefaultsBase, AtlasPersonBase, Entity):
    type_name: str = "m4i_person"

    @classmethod
    def get_type_def(cls):
        return atlas_person_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the systems referenced by this person
        """
        references = self.attributes.source

        return filter(None, references)
# END AtlasPerson
