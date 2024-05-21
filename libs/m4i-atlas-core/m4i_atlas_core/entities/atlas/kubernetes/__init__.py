from ..core import TypesDef
from .KubernetesEnvironment import *
from .KubernetesCluster import *
from .KubernetesNamespace import *
from .KubernetesCronjob import *
from .KubernetesDeployment import *
from .KubernetesPod import *
from ..processes.MicroserviceProcess import *
from ..processes.IngressControllerProcess import *
from ..processes.IngressObjectProcess import *
from ..processes.KubernetesServiceProcess import *
from ..processes.ApiOperationProcess import *

kubernetes_types_def = TypesDef(
    entity_defs=[
        kubernetes_environment_def,
        kubernetes_cluster_def,
        kubernetes_namespace_def,
        kubernetes_deployment_def,
        kubernetes_cronjob_def,
        kubernetes_pod_def,
        microservice_process_def,
        api_operation_process_def,
        ingress_controller_process_def,
        ingress_object_process_def,
        kubernetes_service_process_def,

    ],
    relationship_defs=[
        m4i_kcluster_kenvironment_rel_def,
        m4i_kcluster_knamespace_rel_def,
        m4i_knamespace_kdeployment_rel_def,
        m4i_knamespace_kcronjob_rel_def,
        m4i_kcronjob_kpod_rel_def,
        m4i_kdeployment_kpod_rel_def,
        m4i_msprocess_aoprocess_rel_def,
        m4i_kcluster_icprocess_rel_def,
        m4i_knamespace_ioprocess_rel_def,
        m4i_icprocess_ioprocess_rel_def,
        m4i_knamespace_ksprocess_rel_def,
        m4i_ioprocess_ksprocess_rel_def,
        m4i_ksprocess_msprocess_rel_def,
        m4i_system_msprocess_rel_def,
    ]
)

kubernetes_entity_types = {
    "m4i_kubernetes_environment": KubernetesEnvironment,
    "m4i_kubernetes_cluster": KubernetesCluster,
    "m4i_kubernetes_namespace": KubernetesNamespace,
    "m4i_kubernetes_cronjob": KubernetesCronjob,
    "m4i_kubernetes_deployment": KubernetesDeployment,
    "m4i_kubernetes_pod": KubernetesPod,
    "m4i_microservice_process": MicroserviceProcess,
    "m4i_api_operation_process": ApiOperationProcess,
    "m4i_kubernetes_service_process": KubernetesServiceProcess,
    "m4i_ingress_object_process": IngressObjectProcess,
    "m4i_ingress_controller_process": IngressControllerProcess

}
