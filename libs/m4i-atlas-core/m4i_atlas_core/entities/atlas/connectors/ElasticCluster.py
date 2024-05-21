from dataclasses import dataclass
from typing import Optional, Iterable, List

from dataclasses_json import LetterCase, dataclass_json
from ..core import (AttributeDef,
                    EntityDef, TypeCategory,
                    Cardinality, RelationshipDef, RelationshipEndDef, ObjectId)

from ..data_dictionary import (BusinessSystem, BusinessSystemAttributesBase,
                                              BusinessSystemAttributesDefaultsBase, BusinessSystemBase,
                                              BusinessSystemAttributes, BusinessSystemDefaultsBase)

elastic_cluster_super_type = ["m4i_system"]

elastic_cluster_attributes_def = [
    AttributeDef(
        name="shardCount",
        type_name="int"
    ),
    AttributeDef(
        name="replicaCount",
        type_name="int"
    ),
    AttributeDef(
        name="kibanaSpace",
        type_name="array<m4i_kibana_space>",
        cardinality=Cardinality.SET
    )

]

elastic_cluster_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_elastic_cluster",
    description="A type definition for a generic Elastic Cluster in the context of models4insight.com",
    type_version="1.0",
    super_types=elastic_cluster_super_type,
    attribute_defs=elastic_cluster_attributes_def
)

end_1_elasticcluster_kibanaspace = RelationshipEndDef(
    type="m4i_elastic_cluster",
    name="kibanaSpace",
    cardinality=Cardinality.SET
)
end_2_elasticcluster_kibanaspace = RelationshipEndDef(
    type="m4i_kibana_space",
    name="elasticCluster"
)

m4i_elastic_cluster_kibanaspace_rel_def = RelationshipDef(
    end_def1=end_1_elasticcluster_kibanaspace,
    end_def2=end_2_elasticcluster_kibanaspace,
    name="m4i_kibana_space_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticClusterAttributesBase(BusinessSystemAttributesBase):
    pass


# END ElasticClusterAttributesBase

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticClusterAttributesDefaultsBase(BusinessSystemAttributesDefaultsBase):
    shard_count: Optional[int] = None
    replica_count: Optional[int] = None


# END ElasticClusterAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticClusterAttributes(BusinessSystemAttributes,
                               ElasticClusterAttributesDefaultsBase,
                               ElasticClusterAttributesBase):
    pass


# END ElasticClusterAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticClusterBase(BusinessSystemBase):
    attributes: ElasticClusterAttributes


# END ElasticClusterBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticClusterDefaultsBase(BusinessSystemDefaultsBase):
    pass


# END ElasticClusterDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticCluster(BusinessSystem,
                     ElasticClusterDefaultsBase,
                     ElasticClusterBase):
    type_name: str = "m4i_elastic_cluster"

    @classmethod
    def get_type_def(cls):
        return elastic_cluster_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Elastic Cluster:
        * Kibana Space
        """

        references = [*super().get_referred_entities()]

        return filter(None, references)
    # END get_referred_entities

# END ElasticCluster
