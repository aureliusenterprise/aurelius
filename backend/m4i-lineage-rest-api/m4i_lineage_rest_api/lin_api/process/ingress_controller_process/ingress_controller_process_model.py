from dataclasses import dataclass, field
from dataclasses_json import LetterCase, dataclass_json, DataClassJsonMixin
from m4i_atlas_core import ObjectId, M4IAttributes, IngressControllerProcessRelationshipAttributes
from m4i_atlas_core.entities.atlas.processes.IngressControllerProcess import (
    IngressControllerProcess as CoreIngressControllerProcess,
    IngressControllerProcessAttributes as CoreIngressControllerProcessAttributes)
from typing import List, Optional

from ..generic_process.generic_process_model import GenericProcessBase, GenericProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressControllerProcessBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    cluster: str


# END IngressControllerProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressControllerProcessDefaultsBase(GenericProcessDefaultsBase):
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    ingress_object: List[str] = field(default_factory=list)


# END IngressControllerProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressControllerProcess(
    IngressControllerProcessDefaultsBase,
    IngressControllerProcessBase
):
    def convert_to_atlas(self) -> CoreIngressControllerProcess:
        """
        Returns a corresponding Atlas `IngressControllerProcess` instance.
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

        attributes = CoreIngressControllerProcessAttributes(
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

        if bool(self.ingress_object):
            ingress_object: List[ObjectId] = []
            for so in self.ingress_object:
                ingress_object_unique_attributes = M4IAttributes(
                    qualified_name=so
                )
                ingress_object.append(ObjectId(
                    type_name="m4i_ingress_object_process",
                    unique_attributes=ingress_object_unique_attributes
                ))
            # END FOR
            attributes.ingress_object = ingress_object
        # END

        cluster: List[ObjectId] = []

        cluster_unique_attributes = M4IAttributes(
            qualified_name=self.cluster
        )
        cluster.append(ObjectId(
            type_name="m4i_kubernetes_cluster",
            unique_attributes=cluster_unique_attributes
        ))

        relationship_attributes = IngressControllerProcessRelationshipAttributes(
            cluster=cluster
        )

        entity = CoreIngressControllerProcess(
            attributes=attributes,
            relationship_attributes=relationship_attributes
        )

        return entity
    # END convert_to_atlas
# END IngressControllerProcess
