from .ConfluentEnvironment import *
from .ElasticCluster import *
from .ElasticField import *
from .ElasticIndex import *
from .KafkaCluster import *
from .KafkaField import *
from .KafkaTopic import *
from .KibanaSpace import *
from .KSQL import *
from .ConfluentCloud import *
from .Dashboard import *
from .IndexPattern import *
from .Visualization import *

from ..core import TypesDef

connectors_types_def = TypesDef(

    entity_defs=[
        confluent_environment_def,
        elastic_cluster_def,
        elastic_field_def,
        elastic_index_def,
        kafka_field_def,
        kafka_topic_def,
        kafka_cluster_def,
        kibana_space_def,
        ksql_def,
        confluent_cloud_def,
        dashboard_def,
        visualization_def,
        index_pattern_def
    ],
    relationship_defs=[
        m4i_kcluster_cenvironment_rel_def,
        m4i_elastic_cluster_kibanaspace_rel_def,
        m4i_kafkatopic_ksql_rel_def,
        m4i_ccloud_cenvironment_rel_def,
        m4i_kibana_dashboard_rel_def,
        m4i_person_dashboard_rel_def,
        m4i_person_index_pattern_rel_def,
        m4i_person_visualization_rel_def,
        m4i_elastic_cluster_dashboard_rel_def
    ]
)

connectors_entity_types = {
    "m4i_confluent_environment": ConfluentEnvironment,
    "m4i_elastic_cluster": ElasticCluster,
    "m4i_elastic_field": ElasticField,
    "m4i_elastic_index": ElasticIndex,
    "m4i_kafka_cluster": KafkaCluster,
    "m4i_kafka_field": KafkaField,
    "m4i_kafka_topic": KafkaTopic,
    "m4i_kibana_space": KibanaSpace,
    "m4i_ksql": KSQL,
    "m4i_confluent_cloud": ConfluentCloud,
    "m4i_dashboard": Dashboard,
    "m4i_index_pattern": IndexPattern,
    "m4i_visualization": Visualization
}
