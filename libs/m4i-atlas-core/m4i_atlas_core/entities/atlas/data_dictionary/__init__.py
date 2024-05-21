from ..core import TypesDef
from ..m4i.BusinessArchimate import *
from ..m4i.BusinessReferenceable import *
from ..m4i.BusinessSource import *
from ..m4i.BusinessGovDataQuality import (BusinessGovDataQuality, data_quality_gov_def)
from ..processes.GenericProcess import (GenericProcess, generic_process_def,
                                        m4i_person_gprocess_rel_def,
                                        m4i_system_process_rel_def)
from .AtlasPerson import *
from .BusinessCollection import *
from .BusinessDataAttribute import *
from .BusinessDataDomain import *
from .BusinessDataEntity import *
from .BusinessDataQuality import *
from .BusinessDataset import *
from .BusinessField import *
from .BusinessSystem import *

data_dictionary_types_def = TypesDef(
    entity_defs=[
        m4i_referenceable_def,
        archimate_project_def,
        business_source_def,
        atlas_person_def,
        data_domain_def,
        data_entity_def,
        data_attribute_def,
        atlas_system_def,
        atlas_collection_def,
        atlas_dataset_def,
        data_field_def,
        data_quality_def,
        generic_process_def,
        data_quality_gov_def
    ],
    relationship_defs=[
        m4i_psystem_csystem_rel_def,
        m4i_collection_system_rel_def,
        m4i_pdataset_cdataset_rel_def,
        m4i_dataset_field_rel_def,
        m4i_entity_attribute_rel_def,
        m4i_business_owner_attribute_rel_def,
        m4i_steward_attribute_rel_def,
        m4i_field_attribute_rel_def,
        m4i_dataset_collection_rel_def,
        m4i_domain_entity_rel_def,
        m4i_business_owner_entity_rel_def,
        m4i_steward_entity_rel_def,
        m4i_pentity_centity_rel_def,
        m4i_dataQuality_fields_rel_def,
        m4i_archimate_project_rel_def,
        m4i_business_source_rel_def,
        m4i_pfield_cfield_rel_def,
        m4i_lead_entity_rel_def,
        m4i_person_gprocess_rel_def,
        m4i_system_process_rel_def
    ],
    classification_defs=[
        m4i_classification_pii,
        m4i_classification_key_data,
        m4i_classification_low_risk,
        m4i_classification_medium_risk,
        m4i_classification_high_risk
    ]
)

data_dictionary_entity_types = {
    "m4i_referenceable": BusinessReferenceable,
    "m4i_archimate_project": BusinessArchimate,
    "m4i_source": BusinessSource,
    "m4i_person": AtlasPerson,
    "m4i_data_domain": BusinessDataDomain,
    "m4i_data_entity": BusinessDataEntity,
    "m4i_data_attribute": BusinessDataAttribute,
    "m4i_field": BusinessField,
    "m4i_dataset": BusinessDataset,
    "m4i_collection": BusinessCollection,
    "m4i_system": BusinessSystem,
    "m4i_data_quality": BusinessDataQuality,
    "m4i_generic_process": GenericProcess,
    "m4i_gov_data_quality": BusinessGovDataQuality
}
