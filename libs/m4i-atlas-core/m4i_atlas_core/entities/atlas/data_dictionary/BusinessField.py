from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Attributes, Cardinality, Entity, EntityBase,
                    EntityDef, EntityDefaultsBase, ObjectId, PropagateTags,
                    RelationshipDef, RelationshipEndDef, TypeCategory)
from ..m4i.M4IAttributes import M4IAttributesBase

data_field_attributes_def = [
    AttributeDef(
        name="name",
        type_name="string",
        description="The unique functional name of the data field",
        display_name="Name"
    ),
    AttributeDef(
        name="definition",
        type_name="string",
        description="The definition of the data field determined by the data steward and data owner",
        display_name="Definition"
    ),
    AttributeDef(
        name="fieldType",
        type_name="string",
        description="The classification of the data type of the field",
        display_name="Field Type"
    ),
    AttributeDef(
        name="hasContent",
        type_name="string",
        description="Content Structure for a Field",
        display_name="hasContent"
    ),
    AttributeDef(
        name="optionalField",
        type_name="string",
        description="Optional field for additional value",
        display_name="optionalField"
    ),
    AttributeDef(
        name="datasets",
        type_name="array<m4i_dataset>",
        is_indexable=False,
        description="The name of the dataset to which the field belongs to",
        display_name="Dataset",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="attributes",
        type_name="array<m4i_data_attribute>",
        is_indexable=False,
        description="The functional name of the data attribute that the data field belongs to",
        display_name="Data Attribute",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="steward",
        type_name="array<m4i_person>",
        is_indexable=False,
        description="The business data steward of the data field",
        display_name="Business Data Steward",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="parentField",
        type_name="array<m4i_field>",
        is_indexable=False,
        description="The functional names of the field that this field belongs to",
        display_name="Parent Field",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="childField",
        type_name="array<m4i_field>",
        is_indexable=False,
        description="The functional names of the field that this field belongs to",
        display_name="Child Field",
        cardinality=Cardinality.SET
    ),
]

data_field_super_type = ["m4i_referenceable"]

data_field_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="A type definition for a generic data field",
    name="m4i_field",
    type_version="1.0",
    attribute_defs=data_field_attributes_def,
    super_types=data_field_super_type
)

end_1_dataset_field_attribute = RelationshipEndDef(
    type="m4i_dataset",
    name="fields",
    cardinality=Cardinality.SET
)
end_2_dataset_field_attribute = RelationshipEndDef(
    type="m4i_field",
    name="datasets",
    cardinality=Cardinality.SET
)

dataset_field_typeInfo_attribute_def = [AttributeDef(
    name="typeInformation",
    type_name="string",
    display_name="Type Information"
)]

m4i_dataset_field_rel_def = RelationshipDef(
    end_def1=end_1_dataset_field_attribute,
    end_def2=end_2_dataset_field_attribute,
    name="m4i_field_assignment",
    category=TypeCategory.RELATIONSHIP,
    attribute_defs=dataset_field_typeInfo_attribute_def,
    propagate_tags=PropagateTags.TWO_TO_ONE,
    type_version="1.0",
    description="The relationship between the data field and the dataset"
)

end_1_field_attribute = RelationshipEndDef(
    type="m4i_field",
    name="attributes",
    cardinality=Cardinality.SET
)
end_2_field_attribute = RelationshipEndDef(
    type="m4i_data_attribute",
    name="fields",
    cardinality=Cardinality.SET
)

m4i_field_attribute_rel_def = RelationshipDef(
    end_def1=end_1_field_attribute,
    end_def2=end_2_field_attribute,
    name="m4i_data_attribute_field_assignment",
    propagate_tags=PropagateTags.TWO_TO_ONE,
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the data attribute and the data field"
)

# Parent and Child Field
end_1_pfield_cfield = RelationshipEndDef(
    type="m4i_field",
    name="parentField",
    cardinality=Cardinality.SET
)
end_2_pfield_cfield = RelationshipEndDef(
    type="m4i_field",
    name="childField"

)

m4i_pfield_cfield_rel_def = RelationshipDef(
    end_def1=end_1_pfield_cfield,
    end_def2=end_2_pfield_cfield,
    name="m4i_field_parent_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the data field to other data entities"
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessFieldAttributesBase(M4IAttributesBase):
    name: str
# END BusinessFieldAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessFieldAttributesDefaultsBase(Attributes):
    field_type: Optional[str] = None
    has_content: Optional[str] = None
    optional_field: Optional[str] = None
    definition: Optional[str] = None
    data_quality: List[ObjectId] = field(default_factory=list)
    steward: List[ObjectId] = field(default_factory=list)
    parent_field: List[ObjectId] = field(default_factory=list)
    child_field: List[ObjectId] = field(default_factory=list)
    attributes: List[ObjectId] = field(default_factory=list)
    source: List[ObjectId] = field(default_factory=list)
    datasets: List[ObjectId] = field(default_factory=list)
# END BusinessFieldAttributesDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessFieldAttributes(BusinessFieldAttributesDefaultsBase, BusinessFieldAttributesBase):
    pass
# END BusinessFieldAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessFieldBase(EntityBase):
    attributes: BusinessFieldAttributes
# END BusinessFieldBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessFieldDefaultsBase(EntityDefaultsBase):
    pass
# END BusinessFieldDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessField(BusinessFieldDefaultsBase, BusinessFieldBase, Entity):
    type_name: str = "m4i_field"

    @classmethod
    def get_type_def(cls):
        return data_field_def

    def get_parents(self) -> Iterable[ObjectId]:
        return [*self.attributes.parent_field, *self.attributes.datasets]
    # END get_parents

    def get_children(self) -> Iterable[ObjectId]:
        return [*self.attributes.child_field, *self.attributes.data_quality]
    # END get_children

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this data field:
        * Dataset
        * Data Attribute
        * Steward
        * Parent Field
        """
        references = [
            *self.attributes.datasets,
            *self.attributes.attributes,
            *self.attributes.steward
        ]

        if self.attributes.parent_field is not None:
            references = [*references, *self.attributes.parent_field]
        # END IF

        if self.attributes.child_field is not None:
            references = [*references, *self.attributes.child_field]
        # END IF

        if self.attributes.source is not None:
            references = [*references, *self.attributes.source]
        # END IF

        if self.attributes.data_quality is not None:
            references = [*references, *self.attributes.data_quality]
        # END IF

        return filter(None, references)
    # END get_referred_entities

# END BusinessField
