from typing import Dict, Type

from .GenericProcess import (
    GenericProcess,
    GenericProcessAttributes,
    GenericProcessAttributesBase,
    GenericProcessAttributesDefaultsBase,
    GenericProcessBase,
    GenericProcessDefaultsBase,
    end_1_person_gprocess,
    end_1_system_msprocess,
    end_2_person_gprocess,
    end_2_system_msprocess,
    generic_process_attributes_def,
    generic_process_def,
    generic_process_super_type,
    m4i_person_gprocess_rel_def,
    m4i_system_process_rel_def,
)
from .ConnectorProcess import (
    ConnectorProcess,
    ConnectorProcessAttributes,
    ConnectorProcessAttributesBase,
    ConnectorProcessAttributesDefaultsBase,
    ConnectorProcessBase,
    ConnectorProcessDefaultsBase,
    connector_process_attributes_def,
    connector_process_def,
    connector_process_super_type,
)

from .IngressControllerProcess import IngressControllerProcessRelationshipAttributes
from .IngressObjectProcess import IngressObjectProcessRelationshipAttributes
from .KubernetesServiceProcess import KubernetesServiceProcessRelationshipAttributes
from .MicroserviceProcess import (
    MicroserviceProcess,
    MicroserviceProcessAttributes,
    MicroserviceProcessAttributesBase,
    MicroserviceProcessAttributesDefaultsBase,
    MicroserviceProcessBase,
    MicroserviceProcessDefaultsBase,
)

__all__ = [
    "ConnectorProcess",
    "ConnectorProcessAttributes",
    "ConnectorProcessAttributesBase",
    "ConnectorProcessAttributesDefaultsBase",
    "ConnectorProcessBase",
    "ConnectorProcessDefaultsBase",
    "GenericProcess",
    "GenericProcessAttributes",
    "GenericProcessAttributesBase",
    "GenericProcessAttributesDefaultsBase",
    "GenericProcessBase",
    "GenericProcessDefaultsBase",
    "IngressControllerProcessRelationshipAttributes",
    "IngressObjectProcessRelationshipAttributes",
    "KubernetesServiceProcessRelationshipAttributes",
    "MicroserviceProcess",
    "MicroserviceProcessAttributes",
    "MicroserviceProcessAttributesBase",
    "MicroserviceProcessAttributesDefaultsBase",
    "MicroserviceProcessBase",
    "MicroserviceProcessDefaultsBase",
    "connector_process_attributes_def",
    "connector_process_def",
    "connector_process_super_type",
    "end_1_person_gprocess",
    "end_1_system_msprocess",
    "end_2_person_gprocess",
    "end_2_system_msprocess",
    "generic_process_attributes_def",
    "generic_process_def",
    "generic_process_super_type",
    "m4i_person_gprocess_rel_def",
    "m4i_system_process_rel_def",
    # Aggregate type definitions
    "process_entity_types",
    "process_entity_type_mapping",
    "process_types_def",
]

from ..core import Entity, TypesDef

# Entity types list for registration
process_entity_types = [generic_process_def, connector_process_def]

# Aggregate TypesDef for API calls
process_types_def = TypesDef(
    entity_defs=[generic_process_def, connector_process_def],
    relationship_defs=[m4i_person_gprocess_rel_def, m4i_system_process_rel_def],
)

# Entity type mapping for register_atlas_entity_types (Dict[str, Type[Entity]])
process_entity_type_mapping: Dict[str, Type[Entity]] = {
    "GenericProcess": GenericProcess,
    "ConnectorProcess": ConnectorProcess,
}
