from dataclasses import dataclass
from typing import Iterable, Optional, List

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, EntityDef, ObjectId,
                    TypeCategory)
from .GenericProcess import (GenericProcess,
                             GenericProcessAttributes,
                             GenericProcessAttributesBase,
                             GenericProcessAttributesDefaultsBase,
                             GenericProcessBase,
                             GenericProcessDefaultsBase)

connector_process_super_type = ["m4i_generic_process"]

connector_process_attributes_def = [
    AttributeDef(
        name="connectorType",
        type_name="string"
    ),
    AttributeDef(
        name="server",
        type_name="string"
    )
]

connector_process_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_connector_process",
    description="A type definition for a connector process in the context of models4insight.com",
    type_version="1.0",
    super_types=connector_process_super_type,
    attribute_defs=connector_process_attributes_def
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConnectorProcessAttributesBase(GenericProcessAttributesBase):
    pass


# END ConnectorProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConnectorProcessAttributesDefaultsBase(GenericProcessAttributesDefaultsBase):
    connector_type: Optional[str] = None
    server: Optional[str] = None


# END ConnectorProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConnectorProcessAttributes(GenericProcessAttributes,
                                 ConnectorProcessAttributesDefaultsBase,
                                 ConnectorProcessAttributesBase):
    pass


# END ConnectorProcessAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConnectorProcessBase(GenericProcessBase):
    attributes: ConnectorProcessAttributes


# END ConnectorProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConnectorProcessDefaultsBase(GenericProcessDefaultsBase):
    pass


# END ConnectorProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConnectorProcess(GenericProcess,
                       ConnectorProcessDefaultsBase,
                       ConnectorProcessBase
                       ):
    type_name: str = "m4i_connector_process"

    @classmethod
    def get_type_def(cls):
        return connector_process_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this connector process:
        """

        references = [*super().get_referred_entities()]

        return filter(None, references)
    # END get_referred_entities

# END ConnectorProcess
