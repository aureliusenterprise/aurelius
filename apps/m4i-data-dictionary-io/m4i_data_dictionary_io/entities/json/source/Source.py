from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from m4i_atlas_core import BusinessSource, BusinessSourceAttributes
from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class SourceBase(BaseObject):
    name: str


# END SourceBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class SourceDefaultsBase(DataClassJsonMixin):
    hash_code: Optional[str] = None
    branch: Optional[str] = None


# END SourceDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class Source(SourceDefaultsBase, SourceBase, ToAtlasConvertible[BusinessSource]):
    def convert_to_atlas(self) -> BusinessSource:
        """
        Returns a corresponding Atlas `BusinessSource` instance.
        """

        attributes = BusinessSourceAttributes(
            name=self.name,
            qualified_name=self._qualified_name(),
            hash_code=self.hash_code,
            branch=self.branch,
        )

        entity = BusinessSource(
            attributes=attributes  # type: ignore
        )

        return entity

    # END convert_to_atlas
    def _qualified_name(self):
        """
        Returns the qualified name of the entity based on its `name`,
        optionally including `branch` and `hash_code` suffixes.
        """
        result = self.name
        if self.branch:
            result += "@" + self.branch
        if self.hash_code:
            result += "@" + self.hash_code
        return result

    # END _qualified_name


# END Source
