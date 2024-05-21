from dataclasses import dataclass
from typing import Optional, Iterable, List

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef,
                    EntityDef,
                    ObjectId, TypeCategory, Cardinality,
                    RelationshipEndDef, RelationshipDef
                    )

from ..m4i.BusinessReferenceable import (BusinessReferenceable, BusinessReferenceableAttributesBase,
                                         BusinessReferenceableAttributesDefaultsBase,
                                         BusinessReferenceableBase,
                                         BusinessReferenceableAttributes, BusinessReferenceableDefaultsBase)

ksql_super_type = ["m4i_referenceable"]

ksql_attributes_def = [
    AttributeDef(
        name="name",
        type_name="string"
    ),
    AttributeDef(
        name="valueFormat",
        type_name="string"
    ),
    AttributeDef(
        name="query",
        type_name="string"
    ),
    AttributeDef(
        name="properties",
        type_name="string"
    ),
    AttributeDef(
        name="kafkaTopic",
        type_name="array<m4i_kafka_topic>",
        cardinality=Cardinality.SET
    )
]

ksql_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_ksql",
    description="A type definition for a generic Kafka Sql in the context of models4insight.com",
    type_version="1.0",
    super_types=ksql_super_type,
    attribute_defs=ksql_attributes_def
)

end_1_kafkatopic_ksql = RelationshipEndDef(
    type="m4i_kafka_topic",
    name="ksqlApps",
    cardinality=Cardinality.SET
)
end_2_kafkatopic_ksql = RelationshipEndDef(
    type="m4i_ksql",
    name="kafkaTopic"
)

m4i_kafkatopic_ksql_rel_def = RelationshipDef(
    end_def1=end_1_kafkatopic_ksql,
    end_def2=end_2_kafkatopic_ksql,
    name="m4i_kafkatopic_ksql_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KSQLAttributesBase(BusinessReferenceableAttributesBase):
    name: str
    kafka_topic: List[ObjectId]


# END KSQLAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KSQLAttributesDefaultsBase(BusinessReferenceableAttributesDefaultsBase):
    value_format: Optional[str] = None
    query: Optional[str] = None
    properties: Optional[str] = None

# END KSQLAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KSQLAttributes(BusinessReferenceableAttributes,
                     KSQLAttributesDefaultsBase, KSQLAttributesBase):
    pass


# END KSQLAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KSQLBase(BusinessReferenceableBase):
    attributes: KSQLAttributes


# END KSQLBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KSQLDefaultsBase(BusinessReferenceableDefaultsBase):
    pass


# END KSQLDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KSQL(BusinessReferenceable,
           KSQLDefaultsBase,
           KSQLBase):
    type_name: str = "m4i_ksql"

    @classmethod
    def get_type_def(cls):
        return ksql_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this KSQL:
        * Kafka Topic
        """
        references = [
            *super().get_referred_entities(),
            *self.attributes.kafka_topic
        ]

        return filter(None, references)
    # END get_referred_entities
# END KSQL
