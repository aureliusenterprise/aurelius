from typing import Dict, Type

from .M4IAttributes import M4IAttributes, M4IAttributesBase
from .BusinessSource import (
    BusinessSource,
    BusinessSourceAttributes,
    BusinessSourceAttributesBase,
    BusinessSourceAttributesDefaultsBase,
    BusinessSourceBase,
    BusinessSourceDefaultsBase,
    BusinessSourceRelationshipAttributes,
    business_source_attributes_def,
    business_source_def,
    business_source_super_type,
    end_1_source_changelog,
    end_2_source_references,
    m4i_business_source_rel_def,
)
from .BusinessArchimate import (
    BusinessArchimate,
    BusinessArchimateAttributes,
    BusinessArchimateAttributesBase,
    BusinessArchimateAttributesDefaultsBase,
    BusinessArchimateBase,
    BusinessArchimateDefaultsBase,
    archimate_project_attributes_def,
    archimate_project_def,
    archimate_project_super_type,
    end_1_referenceable_projects,
    end_2_archimate_projects,
    m4i_archimate_project_rel_def,
)
from .BusinessReferenceable import (
    BusinessReferenceable,
    BusinessReferenceableAttributes,
    BusinessReferenceableAttributesBase,
    BusinessReferenceableAttributesDefaultsBase,
    BusinessReferenceableBase,
    BusinessReferenceableDefaultsBase,
    m4i_referenceable_attributes_def,
    m4i_referenceable_def,
    m4i_referenceable_super_type,
)
from .BusinessGovDataQuality import (
    BusinessGovDataQuality,
    BusinessGovDataQualityAttributes,
    BusinessGovDataQualityAttributesBase,
    BusinessGovDataQualityAttributesDefaultsBase,
    BusinessGovDataQualityBase,
    BusinessGovDataQualityDefaultsBase,
    data_quality_gov_attributes_def,
    data_quality_gov_def,
    data_quality_super_type,
)

__all__ = [
    "BusinessArchimate",
    "BusinessArchimateAttributes",
    "BusinessArchimateAttributesBase",
    "BusinessArchimateAttributesDefaultsBase",
    "BusinessArchimateBase",
    "BusinessArchimateDefaultsBase",
    "BusinessGovDataQuality",
    "BusinessGovDataQualityAttributes",
    "BusinessGovDataQualityAttributesBase",
    "BusinessGovDataQualityAttributesDefaultsBase",
    "BusinessGovDataQualityBase",
    "BusinessGovDataQualityDefaultsBase",
    "BusinessReferenceable",
    "BusinessReferenceableAttributes",
    "BusinessReferenceableAttributesBase",
    "BusinessReferenceableAttributesDefaultsBase",
    "BusinessReferenceableBase",
    "BusinessReferenceableDefaultsBase",
    "BusinessSource",
    "BusinessSourceAttributes",
    "BusinessSourceAttributesBase",
    "BusinessSourceAttributesDefaultsBase",
    "BusinessSourceBase",
    "BusinessSourceDefaultsBase",
    "BusinessSourceRelationshipAttributes",
    "M4IAttributes",
    "M4IAttributesBase",
    "archimate_project_attributes_def",
    "archimate_project_def",
    "archimate_project_super_type",
    "business_source_attributes_def",
    "business_source_def",
    "business_source_super_type",
    "data_quality_gov_attributes_def",
    "data_quality_gov_def",
    "data_quality_super_type",
    "end_1_referenceable_projects",
    "end_1_source_changelog",
    "end_2_archimate_projects",
    "end_2_source_references",
    "m4i_archimate_project_rel_def",
    "m4i_business_source_rel_def",
    "m4i_referenceable_attributes_def",
    "m4i_referenceable_def",
    "m4i_referenceable_super_type",
    # Aggregate type definitions
    "m4i_entity_types",
    "m4i_entity_type_mapping",
    "m4i_types_def",
]

from ..core import Entity, TypesDef

# Entity types list for registration
m4i_entity_types = [archimate_project_def, m4i_referenceable_def, data_quality_gov_def, business_source_def]

# Aggregate TypesDef for API calls
m4i_types_def = TypesDef(
    entity_defs=[archimate_project_def, m4i_referenceable_def, data_quality_gov_def, business_source_def],
    relationship_defs=[m4i_archimate_project_rel_def, m4i_business_source_rel_def],
)

# Entity type mapping for register_atlas_entity_types (Dict[str, Type[Entity]])
m4i_entity_type_mapping: Dict[str, Type[Entity]] = {
    "BusinessArchimate": BusinessArchimate,
    "BusinessReferenceable": BusinessReferenceable,
    "BusinessGovDataQuality": BusinessGovDataQuality,
    "BusinessSource": BusinessSource,
}
