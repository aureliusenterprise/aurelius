from dataclasses import dataclass, field
from dataclasses_json import LetterCase, dataclass_json, DataClassJsonMixin
from m4i_atlas_core import ObjectId, M4IAttributes, IngressObjectProcessRelationshipAttributes
from m4i_atlas_core.entities.atlas.processes.IngressObjectProcess import (
    IngressObjectProcess as CoreIngressObjectProcess,
    IngressObjectProcessAttributes as CoreIngressObjectProcessAttributes)
from typing import List, Optional

from ..generic_process.generic_process_model import GenericProcessBase, GenericProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressObjectProcessBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    namespace: str


# END IngressObjectProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressObjectProcessDefaultsBase(GenericProcessDefaultsBase):
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    ingress_controller: Optional[str] = None
    kubernetes_service: List[str] = field(default_factory=list)


# END IngressObjectProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressObjectProcess(
    IngressObjectProcessDefaultsBase,
    IngressObjectProcessBase
):
    def convert_to_atlas(self) -> CoreIngressObjectProcess:
        """
        Returns a corresponding Atlas `IngressObjectProcess` instance.
        """
        inputs: List[ObjectId] = []
        for input in self.inputs:
            input_unique_attributes = M4IAttributes(
                qualified_name=input
            )
            inputs.append(ObjectId(
                type_name="m4i_dataset",
                unique_attributes=input_unique_attributes
            ))
        # END FOR

        outputs: List[ObjectId] = []
        for output in self.outputs:
            output_unique_attributes = M4IAttributes(
                qualified_name=output
            )
            outputs.append(ObjectId(
                type_name="m4i_dataset",
                unique_attributes=output_unique_attributes
            ))
        # END FOR

        attributes = CoreIngressObjectProcessAttributes(
            description=self.description,
            name=self.name,
            inputs=inputs,
            outputs=outputs,
            qualified_name=self.qualified_name,

        )

        if bool(self.process_owner):
            process_owner: List[ObjectId] = []
            process_owner_unique_attributes = M4IAttributes(
                qualified_name=self.process_owner
            )
            process_owner.append(ObjectId(
                type_name="m4i_person",
                unique_attributes=process_owner_unique_attributes
            ))
            attributes.process_owner = process_owner
        # END IF

        if bool(self.kubernetes_service):
            kubernetes_service: List[ObjectId] = []
            for so in self.kubernetes_service:
                kubernetes_service_unique_attributes = M4IAttributes(
                    qualified_name=so
                )
                kubernetes_service.append(ObjectId(
                    type_name="m4i_kubernetes_service_process",
                    unique_attributes=kubernetes_service_unique_attributes
                ))
            # END FOR
            attributes.kubernetes_service = kubernetes_service
        # END
        if bool(self.ingress_controller):
            ingress_controller: List[ObjectId] = []

            ingress_controller_unique_attributes = M4IAttributes(
                qualified_name=self.ingress_controller
            )
            ingress_controller.append(ObjectId(
                type_name="m4i_ingress_controller_process",
                unique_attributes=ingress_controller_unique_attributes
            ))

            attributes.ingress_controller = ingress_controller
        # END

        namespace: List[ObjectId] = []

        namespace_unique_attributes = M4IAttributes(
            qualified_name=self.namespace
        )
        namespace.append(ObjectId(
            type_name="m4i_kubernetes_namespace",
            unique_attributes=namespace_unique_attributes
        ))

        relationship_attributes = IngressObjectProcessRelationshipAttributes(
            namespace=namespace
        )

        entity = CoreIngressObjectProcess(
            attributes=attributes,
            relationship_attributes=relationship_attributes
        )

        return entity
    # END convert_to_atlas
# END IngressObjectProcess
