import copy
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (ElasticField, ElasticFieldAttributes,
                            M4IAttributes, ObjectId)
from typing import Dict, List, Union

from .ElasticIndexTemplateMappingsProperty import ElasticIndexTemplateMappingsProperty


class MappingPropertyUndefinedException(Exception):
    """
    Raised when a property specified in the _meta field cannot be found in the properties field.
    """


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexTemplateMappingsBase(DataClassJsonMixin):
    properties: Dict[str, ElasticIndexTemplateMappingsProperty]
    _meta: Dict[str, Union[str, List[str], dict]]


# END ElasticIndexTemplateMappingsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexTemplateMappingsDefaultsBase(DataClassJsonMixin):
    pass


# END ElasticIndexTemplateMappingsDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexTemplateMappings(
    ElasticIndexTemplateMappingsDefaultsBase,
    ElasticIndexTemplateMappingsBase,
):

    def convert_to_atlas(self, parent_index_qualified_name: str, parent_index_guid: str) -> List[ElasticField]:
        """
        Returns a list of `ElasticField` instances for all fields defined as part of the mapping.
        """

        dataset_unique_attributes = M4IAttributes(
            qualified_name=parent_index_qualified_name
        )

        dataset = [ObjectId(
            type_name="m4i_elastic_index",
            unique_attributes=dataset_unique_attributes,
            guid=parent_index_guid
        )]

        def to_elastic_field(field_key: str, parent_qn: str = None, parent_guid: str = None, meta_nested: dict = None,
                             property_nested: dict = None):

            if parent_qn is None:
                mapping_meta = self._meta.get(field_key)
                mapping_property = self.properties.get(field_key)
                qn = f"{parent_index_qualified_name}--{field_key}"
            else:
                try:
                    mapping_meta = meta_nested.get(field_key)
                except AttributeError:
                    mapping_meta = None
                mapping_property = property_nested.get(field_key)
                qn = f"{parent_qn}--{field_key}"
            attributes = ElasticFieldAttributes(
                qualified_name=qn,
                datasets=dataset,
                name=field_key,
                field_type=mapping_property.type
            )
            if mapping_meta is not None and not isinstance(mapping_meta, dict):
                metas = []
                if isinstance(mapping_meta, str):
                    mapping_meta = [mapping_meta]

                for att in mapping_meta:
                    attribute_unique_attributes = M4IAttributes(
                        qualified_name=att
                    )
                    metas.append(ObjectId(
                        type_name="m4i_data_attribute",
                        unique_attributes=attribute_unique_attributes
                    ))
                attributes.attributes = metas
            if parent_qn is not None:
                parent_field_unique_attributes = M4IAttributes(
                    qualified_name=parent_qn
                )
                parent_field = [(ObjectId(
                    type_name="m4i_elastic_field",
                    guid=parent_guid,
                    unique_attributes=parent_field_unique_attributes
                ))]
                attributes.parent_field = parent_field
                attributes.datasets = None

            elastic_field = ElasticField(
                attributes=attributes
            )
            elastic_ref = copy.deepcopy(elastic_field)
            nested_fields = []
            ref_fields = []
            if mapping_property.properties != {}:
                for nest in mapping_property.properties.keys():
                    field = to_elastic_field(field_key=nest, parent_qn=qn, parent_guid=elastic_field.guid,
                                             meta_nested=mapping_meta,
                                             property_nested=mapping_property.properties)
                    nested_fields = [*nested_fields,
                                     *field[0]]
                    ref_fields = [*ref_fields,
                                  *field[1]]

                elastic_ref.attributes.child_field = nested_fields
            return [elastic_field], [elastic_ref, *ref_fields]

        # END to_elastic_field

        elastic_fields = []
        elastic_fields_ref = []
        for field_key in self.properties.keys():
            field_tuple = to_elastic_field(field_key)
            elastic_fields = [*elastic_fields, *field_tuple[0]]
            elastic_fields_ref = [*elastic_fields_ref, *field_tuple[1]]

        return elastic_fields, elastic_fields_ref
    # END convert_to_atlas
# END ElasticIndexTemplateMappings
