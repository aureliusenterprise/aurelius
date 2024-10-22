from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, BusinessDataEntity, BusinessDataEntityAttributes
from m4i_atlas_core import M4IAttributes
from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataEntityBase(BaseObject):
    data_domain: str
    name: str
# END DataEntityBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataEntityDefaultsBase(DataClassJsonMixin):
    business_owner: Optional[str] = None
    definition: Optional[str] = None
    parent_entity: Optional[str] = None
    steward: Optional[str] = None
    domain_link: Optional[str]= None
    source: Optional[str] = None
# END DataEntityDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataEntity(
    DataEntityDefaultsBase,
    DataEntityBase,
    ToAtlasConvertible[BusinessDataEntity]
):
    def convert_to_atlas(self) -> BusinessDataEntity:
        """
        Returns a corresponding Atlas `BusinessDataEntity` instance.
        """

        data_domain_unique_attributes = M4IAttributes(
            qualified_name=self.data_domain
        )

        data_domain = ObjectId(
            type_name="m4i_data_domain",
            unique_attributes=data_domain_unique_attributes
        )

        attributes = BusinessDataEntityAttributes(
            data_domain=[data_domain],
            definition=self.definition,
            name=self.name,
            qualified_name=self.qualified_name,
        )

        if bool(self.business_owner):
            unique_attributes = M4IAttributes(
                qualified_name=self.business_owner
            )

            business_owner = ObjectId(
                type_name="m4i_person",
                unique_attributes=unique_attributes
            )

            attributes.business_owner = [business_owner]
        # END IF

        if self.has_parent:
            unique_attributes = M4IAttributes(
                qualified_name=self.parent_entity
            )

            parent_entity = ObjectId(
                type_name="m4i_data_entity",
                unique_attributes=unique_attributes
            )

            attributes.parent_entity = [parent_entity]
            if self.domain_link != "Yes":
                attributes.data_domain = None
        # END IF

        if bool(self.steward):
            unique_attributes = M4IAttributes(
                qualified_name=self.steward
            )

            steward = ObjectId(
                type_name="m4i_person",
                unique_attributes=unique_attributes
            )

            attributes.steward = [steward]
        # END IF

        if bool(self.source):
            unique_attributes = M4IAttributes(
                qualified_name=self.source
            )

            source = ObjectId(
                type_name="m4i_source",
                unique_attributes=unique_attributes
            )

            attributes.source = [source]
        # END IF

        entity = BusinessDataEntity(
            attributes=attributes,
        )

        return entity
    # END convert_to_atlas

    def _qualified_name(self):
        """
        Returns the qualified name of the entity based on its parent `data_domain`, its `parent_entity` and its `name`
        """

        return get_qualified_name(
            self.name,
            prefix=self.parent_entity if self.has_parent else self.data_domain
        )
    # END _qualified_name

    @property
    def has_parent(self):
        """
        Returns whether or not this entity has a `parent_entity`
        """
        return bool(self.parent_entity)
    # END has_parent

# END DataEntity
