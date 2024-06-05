from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (ObjectId, M4IAttributes, KSQL as CoreKSQL,
                            KSQLAttributes as CoreKSQLAttributes)
from typing import Optional

from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KSQLBase(DataClassJsonMixin):
    name: str
    kafka_topic: str

    def _qualified_name(self):
        """
        Returns the qualified name of the KSQL based on its `environment`, 'cluster' and 'name'
        """
        # KSQLQualifiedName is based on env, cluster and name
        return get_qualified_name(
            self.name,
            prefix=f'{self.env}--{self.cluster}'

        )
    # END _qualified_name


# END KSQLBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KSQLDefaultsBase(DataClassJsonMixin):
    env: Optional[str] = None
    cluster: Optional[str] = None
    value_format: Optional[str] = None
    query: Optional[str] = None
    properties: Optional[str] = None
    archimate_project: Optional[ObjectId] = None


# END KSQLDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KSQL(
    KSQLDefaultsBase,
    KSQLBase
):

    def convert_to_atlas(self) -> CoreKSQL:
        """
        Returns a corresponding Atlas `KSQL` instance.
        """
        # Object Relationships
        kafka_topic = []
        referencable_unique_attributes = M4IAttributes(
            qualified_name=self.kafka_topic
        )

        kafka_topic.append(ObjectId(
            type_name="m4i_kafka_topic",
            unique_attributes=referencable_unique_attributes
        ))

        attributes = CoreKSQLAttributes(
            kafka_topic=kafka_topic,
            value_format=self.value_format,
            query=self.query,
            properties=self.properties,
            name=self.name,
            qualified_name=self._qualified_name()

        )

        entity = CoreKSQL(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END KSQL
