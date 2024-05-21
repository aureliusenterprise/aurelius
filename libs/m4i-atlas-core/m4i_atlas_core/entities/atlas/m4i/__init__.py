from .M4IAttributes import *
from .BusinessSource import *
from .BusinessArchimate import *
from .BusinessReferenceable import *
from .BusinessGovDataQuality import *

from ..core import TypesDef


m4i_types_def = TypesDef(
    entity_defs=[
        data_quality_gov_def
    ],
    relationship_defs=[
    ]
)

m4i_entity_types = {
    "m4i_gov_data_quality": BusinessGovDataQuality
}
