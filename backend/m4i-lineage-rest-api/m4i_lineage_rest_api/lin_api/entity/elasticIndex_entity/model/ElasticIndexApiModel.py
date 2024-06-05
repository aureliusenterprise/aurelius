from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (ElasticField, ElasticIndex, ElasticIndexAttributes,
                            M4IAttributes, ObjectId)
from typing import List, Optional, Union

from .ElasticIndexTemplateModel import ElasticIndexTemplateModel
from ...ToAtlasConvertible import ToAtlasConvertible


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexApiModelBase(DataClassJsonMixin):
    name: str
    qualified_name: str


# END ElasticIndexApiModelBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexApiModelDefaultsBase(DataClassJsonMixin):
    cluster: Optional[str] = None
    environment: Optional[str] = None
    index_template: Optional[ElasticIndexTemplateModel] = None


# END ElasticIndexApiModelDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexApiModel(
    ElasticIndexApiModelDefaultsBase,
    ElasticIndexApiModelBase,
    ToAtlasConvertible[List[Union[ElasticIndex, ElasticField]]]
):

    def convert_to_atlas(self) -> List[Union[ElasticIndex, ElasticField]]:
        """
        Returns a corresponding Atlas `ElasticIndex` instance, along with a list of `ElasticField` instances representing the fields of the schema.
        """

        collection_unique_attributes = M4IAttributes(
            qualified_name=f"{self.cluster}--data"
        )

        collection = [ObjectId(
            type_name="m4i_collection",
            unique_attributes=collection_unique_attributes,
            guid='-1'
        )]
        cluster_unique_attributes = M4IAttributes(
            qualified_name=f"{self.cluster}"
        )

        cluster = [ObjectId(
            type_name="m4i_elastic_cluster",
            unique_attributes=cluster_unique_attributes,
        )]

        collection_ref = {'-1': {
            "guid": "-1",
            "typeName": "m4i_collection",
            "attributes": {
                "qualifiedName": collection_unique_attributes.qualified_name,
                "systems": cluster,
                "name": collection_unique_attributes.qualified_name
            }
        }}

        attributes = ElasticIndexAttributes(
            name=self.name,
            collections=collection,
            qualified_name=self.qualified_name
        )

        entity = ElasticIndex(
            attributes=attributes
        )

        if self.index_template is not None:
            fields, refs = self.index_template.mappings.convert_to_atlas(self.qualified_name, entity.guid)
            entity.attributes.fields = [*fields]
            for i in refs:
                collection_ref[i.guid] = i
        # END IF
        result = [entity]

        return result, collection_ref
    # END convert_to_atlas

# END ElasticIndexApiModel
