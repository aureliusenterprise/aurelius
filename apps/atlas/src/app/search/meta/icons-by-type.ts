import { faCheckCircle, faCog, faFileImport, faProjectDiagram, faServer, faTable, faTag, faUser, IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { Dictionary } from 'lodash';

export type AtlasTypeIconDefinitionClass =
  | 'business'
  | 'technical'
  | 'technical-process'
  | 'meta';

export interface AtlasTypeIconDefinition {
  icon: IconDefinition;
  classIcon: AtlasTypeIconDefinitionClass;
}

export const iconsByType: Dictionary<AtlasTypeIconDefinition> = {
  m4i_data_attribute: {
    icon: faTag,
    classIcon: 'business'
  },
  m4i_data_entity: {
    icon: faTable,
    classIcon: 'business'
  },
  m4i_data_domain: {
    icon: faProjectDiagram,
    classIcon: 'business'
  },
  m4i_field: {
    icon: faTag,
    classIcon: 'technical'
  },
  m4i_dataset: {
    icon: faTable,
    classIcon: 'technical'
  },
  m4i_collection: {
    icon: faProjectDiagram,
    classIcon: 'technical'
  },
  m4i_system: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_person: {
    icon: faUser,
    classIcon: 'business'
  },
  m4i_dashboard: {
    icon: faTable,
    classIcon: 'technical'
  },
  m4i_generic_process: {
    icon: faCog,
    classIcon: 'technical-process'
  },
  m4i_kafka_topic: {
    icon: faTable,
    classIcon: 'technical'
  },
  m4i_confluent_cloud: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_index_pattern: {
    icon: faProjectDiagram,
    classIcon: 'technical'
  },
  m4i_confluent_environment: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_elastic_index: {
    icon: faTable,
    classIcon: 'technical'
  },
  m4i_visualization: {
    icon: faTable,
    classIcon: 'technical'
  },
  m4i_elastic_cluster: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_connector_process: {
    icon: faCog,
    classIcon: 'technical-process'
  },
  m4i_elastic_field: {
    icon: faTag,
    classIcon: 'technical'
  },
  m4i_kafka_field: {
    icon: faTag,
    classIcon: 'technical'
  },
  m4i_kibana_space: {
    icon: faProjectDiagram,
    classIcon: 'technical'
  },
  m4i_kafka_cluster: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_elastic: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_kubernetes_cluster: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_kubernetes_cronjob: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_kubernetes_deployment: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_kubernetes_environment: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_kubernetes_namespace: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_kubernetes_pod: {
    icon: faServer,
    classIcon: 'technical'
  },
  m4i_data_quality: {
    icon: faCheckCircle,
    classIcon: 'technical'
  },
  m4i_api_operation_process: {
    icon: faCog,
    classIcon: 'technical-process'
  },
  m4i_ingress_controller_process: {
    icon: faCog,
    classIcon: 'technical-process'
  },
  m4i_ingress_object_process: {
    icon: faCog,
    classIcon: 'technical-process'
  },
  m4i_kubenetes_serce_process: {
    icon: faCog,
    classIcon: 'technical-process'
  },
  m4i_microservice_process: {
    icon: faCog,
    classIcon: 'technical-process'
  },
  m4i_gov_data_quality: {
    icon: faCheckCircle,
    classIcon: 'meta'
  },
  m4i_source: {
    icon: faFileImport,
    classIcon: 'meta'
  }
};
