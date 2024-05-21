from ..core import TypesDef
from .GenericProcess import *
from .ConnectorProcess import *


process_types_def = TypesDef(
    entity_defs=[
        generic_process_def,
    ],
    relationship_defs=[
        m4i_person_gprocess_rel_def,
        m4i_system_process_rel_def
    ]
)

process_entity_types = {
    "m4i_generic_process": GenericProcess,
}
