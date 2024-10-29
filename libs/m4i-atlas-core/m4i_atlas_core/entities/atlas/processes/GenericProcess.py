from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Cardinality, Entity, EntityBase, EntityDef,
                    EntityDefaultsBase, ObjectId, RelationshipDef,
                    RelationshipEndDef, TypeCategory)
from ..m4i.M4IAttributes import M4IAttributesBase

generic_process_super_type = ["Process", "m4i_referenceable"]

generic_process_attributes_def = [
    AttributeDef(
        name="processOwner",
        type_name="array<m4i_person>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="system",
        type_name="array<m4i_system>",
        cardinality=Cardinality.SET
    ),
]

generic_process_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_generic_process",
    description="A type definition for a generic process in the context of models4insight.com",
    type_version="1.0",
    super_types=generic_process_super_type,
    attribute_defs=generic_process_attributes_def
)

end_1_person_gprocess = RelationshipEndDef(
    type="m4i_person",
    name="ProcessOwner",
)

end_2_person_gprocess = RelationshipEndDef(
    type="m4i_generic_process",
    name="processOwner"
)

m4i_person_gprocess_rel_def = RelationshipDef(
    end_def1=end_1_person_gprocess,
    end_def2=end_2_person_gprocess,
    name="m4i_process_owner_assignment",
    category=TypeCategory.RELATIONSHIP
)

end_1_system_msprocess = RelationshipEndDef(
    type="m4i_system",
    name="processes",
)

end_2_system_msprocess = RelationshipEndDef(
    type="m4i_generic_process",
    name="system"
)

m4i_system_process_rel_def = RelationshipDef(
    end_def1=end_1_system_msprocess,
    end_def2=end_2_system_msprocess,
    name="m4i_system_process_assignment",
    category=TypeCategory.RELATIONSHIP
)

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenericProcessAttributesBase(M4IAttributesBase):
    name: str
# END GenericProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenericProcessAttributesDefaultsBase():
    process_owner: List[ObjectId] = field(default_factory=list)
    description: Optional[str] = None
    name: Optional[str] = None
    inputs: List[ObjectId] = field(default_factory=list)
    outputs: List[ObjectId] = field(default_factory=list)
    system: List[ObjectId] = field(default_factory=list)
# END GenericProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenericProcessAttributes(GenericProcessAttributesDefaultsBase, GenericProcessAttributesBase):
    pass
# END GenericProcessAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenericProcessBase(EntityBase):
    attributes: GenericProcessAttributes
# END GenericProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenericProcessDefaultsBase(EntityDefaultsBase):
    pass
# END GenericProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenericProcess(GenericProcessDefaultsBase, GenericProcessBase, Entity):
    type_name: str = "m4i_generic_process"

    @classmethod
    def get_type_def(cls):
        return generic_process_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Generic Process:
        process owner
        list of inputs
        list of outputs
        """

        references = [
            *self.attributes.process_owner,
            *self.attributes.inputs,
            *self.attributes.outputs,
            *self.attributes.system
        ]

        return filter(None, references)
    # END get_referred_entities

# END GenericProcess
