from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import AttributeDef, Cardinality, EntityDef, ObjectId, TypeCategory, RelationshipEndDef, RelationshipDef
from ..data_dictionary import (BusinessDataset, BusinessDatasetAttributes,
                               BusinessDatasetAttributesBase,
                               BusinessDatasetAttributesDefaultsBase,
                               BusinessDatasetBase,
                               BusinessDatasetDefaultsBase)

dashboard_super_type = ["m4i_dataset"]

dashboard_attributes_def = [
    AttributeDef(
        name="updatedAt",
        type_name="string"
    ),
    AttributeDef(
        name="version",
        type_name="string"
    ),
    AttributeDef(
        name="creator",
        type_name="array<m4i_person>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="elasticCluster",
        type_name="array<m4i_elastic_cluster>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="kibanaSpace",
        type_name="array<m4i_kibana_space>",
        cardinality=Cardinality.SET
    ),
]

dashboard_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_dashboard",
    description="A type definition for a generic Dashboard in the context of models4insight.com",
    type_version="1.0",
    super_types=dashboard_super_type,
    attribute_defs=dashboard_attributes_def
)
end_1_kibana_dashboard = RelationshipEndDef(
    type="m4i_kibana_space",
    name="dashboards",
)
end_2_kibana_dashboard = RelationshipEndDef(
    type="m4i_dashboard",
    name="kibanaSpace",
)

m4i_kibana_dashboard_rel_def = RelationshipDef(
    end_def1=end_1_kibana_dashboard,
    end_def2=end_2_kibana_dashboard,
    name="m4i_kibana_space_dashboard_assignment",
    category=TypeCategory.RELATIONSHIP
)

end_1_person_dashboard = RelationshipEndDef(
    type="m4i_person",
    name="dashboards",
)
end_2_person_dashboard = RelationshipEndDef(
    type="m4i_dashboard",
    name="creator",
)

m4i_person_dashboard_rel_def = RelationshipDef(
    end_def1=end_1_person_dashboard,
    end_def2=end_2_person_dashboard,
    name="m4i_person_dashboard_assignment",
    category=TypeCategory.RELATIONSHIP
)

end_1_elastic_cluster_dashboard = RelationshipEndDef(
    type="m4i_elastic_cluster",
    name="dashboards",
)
end_2_elastic_cluster_dashboard = RelationshipEndDef(
    type="m4i_dashboard",
    name="elasticCluster",
)

m4i_elastic_cluster_dashboard_rel_def = RelationshipDef(
    end_def1=end_1_elastic_cluster_dashboard,
    end_def2=end_2_elastic_cluster_dashboard,
    name="m4i_elasticCluster_dashboard_assignment",
    category=TypeCategory.RELATIONSHIP
)



@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DashboardAttributesBase(BusinessDatasetAttributesBase):
    pass


# END DashboardAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DashboardAttributesDefaultsBase(BusinessDatasetAttributesDefaultsBase):
    updated_at: Optional[str] = None
    version: Optional[str] = None
    elastic_cluster: List[ObjectId] = field(default_factory=list)
    kibana_space: List[ObjectId] = field(default_factory=list)
    creator: List[ObjectId] = field(default_factory=list)


# END DashboardAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DashboardAttributes(BusinessDatasetAttributes,
                          DashboardAttributesDefaultsBase, DashboardAttributesBase):
    pass


# END DashboardAttributes

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DashboardBase(BusinessDatasetBase):
    attributes: DashboardAttributes


# END DashboardBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DashboardDefaultsBase(BusinessDatasetDefaultsBase):
    pass


# END DashboardDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Dashboard(
    BusinessDataset,
    DashboardDefaultsBase,
    DashboardBase,
):
    type_name: str = "m4i_dashboard"

    @classmethod
    def get_type_def(cls):
        return dashboard_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Dashboard:
        * List of Kibana Space
        * List of Elastic Cluster
        * List of Atlas Person
        """

        references = [
            *super().get_referred_entities(),
            *self.attributes.kibana_space,
            *self.attributes.elastic_cluster,

        ]

        if self.attributes.creator is not None:
            references = [*references, *self.attributes.creator]
        # END IF

        return filter(None, references)
    # END get_referred_entities

# END Dashboard
