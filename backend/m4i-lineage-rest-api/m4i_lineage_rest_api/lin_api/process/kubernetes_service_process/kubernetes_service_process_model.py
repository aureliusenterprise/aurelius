from dataclasses import dataclass, field
from dataclasses_json import LetterCase, dataclass_json, DataClassJsonMixin
from m4i_atlas_core import ObjectId, M4IAttributes, KubernetesServiceProcessRelationshipAttributes
from m4i_atlas_core.entities.atlas.processes.KubernetesServiceProcess import (
    KubernetesServiceProcess as CoreKubernetesServiceProcess,
    KubernetesServiceProcessAttributes as CoreKubernetesServiceProcessAttributes)
from typing import List, Optional

from ..generic_process.generic_process_model import GenericProcessBase, GenericProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesServiceProcessBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    namespace: str


# END KubernetesServiceProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesServiceProcessDefaultsBase(GenericProcessDefaultsBase):
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    microservice: List[str] = field(default_factory=list)
    ingress_object: Optional[str] = None


# END KubernetesServiceProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesServiceProcess(
    KubernetesServiceProcessDefaultsBase,
    KubernetesServiceProcessBase
):
    def convert_to_atlas(self) -> CoreKubernetesServiceProcess:
        """
        Returns a corresponding Atlas `KubernetesServiceProcess` instance.
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

        attributes = CoreKubernetesServiceProcessAttributes(
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
            ingress_object_unique_attributes = M4IAttributes(
                qualified_name=self.ingress_object
            )
            ingress_object.append(ObjectId(
                type_name="m4i_ingress_object_process",
                unique_attributes=ingress_object_unique_attributes
            ))
            attributes.ingress_object = ingress_object
        # END

        if bool(self.microservice):
            microservice: List[ObjectId] = []
            for so in self.microservice:
                microservice_unique_attributes = M4IAttributes(
                    qualified_name=so
                )
                microservice.append(ObjectId(
                    type_name="m4i_microservice_process",
                    unique_attributes=microservice_unique_attributes
                ))
            # END FOR
            attributes.microservice = microservice
        # END
        namespace: List[ObjectId] = []
        namespace_unique_attributes = M4IAttributes(
            qualified_name=self.namespace
        )
        namespace.append(ObjectId(
            type_name="m4i_kubernetes_namespace",
            unique_attributes=namespace_unique_attributes
        ))

        relationship_attributes = KubernetesServiceProcessRelationshipAttributes(
            namespace=namespace
        )

        entity = CoreKubernetesServiceProcess(
            attributes=attributes,
            relationship_attributes=relationship_attributes
        )

        return entity
    # END convert_to_atlas
# END KubernetesServiceProcess
