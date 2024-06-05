from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (ObjectId, M4IAttributes, KibanaSpace as CoreKibanaSpace,
                            KibanaSpaceAttributes as CoreKibanaSpaceAttributes)
from typing import Optional

from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KibanaSpaceBase(DataClassJsonMixin):
    name: str
    elastic_cluster: str

    def _qualified_name(self):
        """
        Returns the qualified name of the KibanaSpace based on its `elastic_cluster`
        """
        # KibanaSpaceQualifiedName is based on elastic_cluster
        return get_qualified_name(
            self.name,
            prefix=self.elastic_cluster
        )
    # END _qualified_name


# END KibanaSpaceBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KibanaSpaceDefaultsBase(DataClassJsonMixin):
    avatar_color: Optional[str] = None
    avatar_initials: Optional[str] = None
    definition: Optional[str] = None


# END KibanaSpaceDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KibanaSpace(
    KibanaSpaceDefaultsBase,
    KibanaSpaceBase
):

    def convert_to_atlas(self) -> CoreKibanaSpace:
        """
        Returns a corresponding Atlas `KibanaSpace` instance.
        """
        elastic_cluster = []
        system_unique_attributes = M4IAttributes(
            qualified_name=self.elastic_cluster
        )

        elastic_cluster.append(ObjectId(
            type_name="m4i_elastic_cluster",
            unique_attributes=system_unique_attributes
        ))

        attributes = CoreKibanaSpaceAttributes(
            systems=elastic_cluster,
            elastic_cluster=elastic_cluster,
            avatar_color=self.avatar_color,
            avatar_initials=self.avatar_initials,
            name=self.name,
            definition=self.definition,
            qualified_name=self._qualified_name()

        )

        entity = CoreKibanaSpace(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END KibanaSpace
