from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core.entities.atlas.connectors import (ElasticCluster as CoreElasticCluster,
                                                      ElasticClusterAttributes as CoreElasticClusterAttributes)
from typing import Optional

from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticClusterBase(DataClassJsonMixin):
    name: str

    def _qualified_name(self):
        """
        Returns the qualified name of the ElasticCluster based on its `confluent_environment`
        """
        # ElasticClusterQualifiedName is based on confluent_environment
        return get_qualified_name(
            self.name
        )
    # END _qualified_name


# END ElasticClusterBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticClusterDefaultsBase(DataClassJsonMixin):
    shard_count: Optional[int] = None
    replica_count: Optional[int] = None


# END ElasticClusterDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticCluster(
    ElasticClusterDefaultsBase,
    ElasticClusterBase
):

    def convert_to_atlas(self) -> CoreElasticCluster:
        """
        Returns a corresponding Atlas `ElasticCluster` instance.
        """

        attributes = CoreElasticClusterAttributes(
            shard_count=self.shard_count,
            replica_count=self.replica_count,
            name=self.name,
            qualified_name=self._qualified_name()
        )

        entity = CoreElasticCluster(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END ElasticCluster
