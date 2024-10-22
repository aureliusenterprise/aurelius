from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, BusinessDataDomain, BusinessDataDomainAttributes

from m4i_atlas_core import M4IAttributes
from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataDomainBase(BaseObject):
    name: str

    def _qualified_name(self):
        """
        Returns the qualified name of the domain based on its `name`
        """

        return get_qualified_name(self.name)
    # END _qualified_name


# END DataDomainBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataDomainDefaultsBase(DataClassJsonMixin):
    definition: Optional[str] = None
    domain_lead: Optional[str] = None
    source: Optional[str] = None


# END DataDomainDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataDomain(
    DataDomainDefaultsBase,
    DataDomainBase,
    ToAtlasConvertible[BusinessDataDomain]
):
    def convert_to_atlas(self) -> BusinessDataDomain:
        """
        Returns a corresponding Atlas `BusinessDataDomain` instance.
        """

        attributes = BusinessDataDomainAttributes(
            definition=self.definition,
            name=self.name,
            qualified_name=self.qualified_name,
            source=self.source
        )

        if bool(self.domain_lead):
            unique_attributes = M4IAttributes(
                qualified_name=self.domain_lead
            )

            domain_lead = ObjectId(
                type_name="m4i_person",
                unique_attributes=unique_attributes
            )

            attributes.domain_lead = [domain_lead]
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

        entity = BusinessDataDomain(
            attributes=attributes,
        )

        return entity
    # END convert_to_atlas
# END DataDomain
