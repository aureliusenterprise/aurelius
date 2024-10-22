from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from m4i_atlas_core import BusinessSource, BusinessSourceAttributes, M4IAttributes, ObjectId
from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SourceBase(BaseObject):
    name: str


# END SourceBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SourceDefaultsBase(DataClassJsonMixin):
    hash_code: Optional[str] = None
    branch: Optional[str] = None
    # change_log: Optional[str] = None


# END SourceDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Source(
    SourceDefaultsBase,
    SourceBase,
    ToAtlasConvertible[BusinessSource]
):
    def convert_to_atlas(self) -> BusinessSource:
        """
        Returns a corresponding Atlas `BusinessSource` instance.
        """
        # change_logs=[]
        # if bool(self.change_log):
        #     unique_attributes = M4IAttributes(
        #         qualified_name=self.change_log
        #     )
        #
        #     change_log = ObjectId(
        #         type_name="m4i_referenceable",
        #         unique_attributes=unique_attributes
        #     )
        #     change_logs = [change_log]
        # # END IF

        attributes = BusinessSourceAttributes(
            name=self.name,
            hash_code=self.hash_code,
            # change_log=change_logs,
            branch=self.branch,
            qualified_name=self._qualified_name(),
        )

        entity = BusinessSource(
            attributes=attributes,
        )

        return entity

    # END convert_to_atlas
    def _qualified_name(self):
        """
        Returns the qualified name of the entity based on its `name`, `GIT branch`, and its `GIT hashcode`
        """
        return f"{self.name}@{self.branch}@{self.hash_code}"
    # END _qualified_name
# END Source
