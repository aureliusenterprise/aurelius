import { archimate3 } from '@models4insight/metamodel';
import {
  ar3Actor,
  ar3ApplicationComponent,
  ar3ArchiDiagramModelReference,
  ar3Artifact,
  ar3Assessment,
  ar3Capability,
  ar3Collaboration,
  ar3CommunicationNetwork,
  ar3Constraint,
  ar3Contract,
  ar3CourseOfAction,
  ar3Deliverable,
  ar3Device,
  ar3DistributionNetwork,
  ar3Driver,
  ar3Equipment,
  ar3Event,
  ar3Facility,
  ar3Function,
  ar3Gap,
  ar3Goal,
  ar3Grouping,
  ar3Interaction,
  ar3Interface,
  ar3Junction,
  ar3Location,
  ar3Material,
  ar3Meaning,
  ar3Node,
  ar3Object,
  ar3Outcome,
  ar3Path,
  ar3Plateau,
  ar3Principle,
  ar3Process,
  ar3Product,
  ar3Representation,
  ar3Requirement,
  ar3Resource,
  ar3Role,
  ar3Service,
  ar3SystemSoftware,
  ar3Value,
  ar3ValueStream,
  ar3WorkPackage,
  lineage_dataset,
  lineage_process,
} from './shapes';

export type IconDefinitionType =
  | 'business'
  | 'application'
  | 'technology'
  | 'physical'
  | 'motivation'
  | 'implementation & migration'
  | 'strategy'
  | 'composite'
  | 'and'
  | 'or'
  | 'link'
  | 'location'
  | 'dataset'
  | 'process';

export interface IconDefinition {
  readonly icon: string;
  readonly type: IconDefinitionType;
}

export type Archimate3IconDefinitions = {
  [tag in
    | keyof typeof archimate3.elements
    | 'ar3_ArchiDiagramModelReference'
    | 'lineage_dataset'
    | 'lineage_process']?: IconDefinition;
};

export const definitions: Archimate3IconDefinitions = {
  ar3_AndJunction: {
    icon: ar3Junction,
    type: 'and',
  },
  ar3_ApplicationCollaboration: {
    icon: ar3Collaboration,
    type: 'application',
  },
  ar3_ApplicationComponent: {
    icon: ar3ApplicationComponent,
    type: 'application',
  },
  ar3_ApplicationEvent: {
    icon: ar3Event,
    type: 'application',
  },
  ar3_ApplicationFunction: {
    icon: ar3Function,
    type: 'application',
  },
  ar3_ApplicationInteraction: {
    icon: ar3Interaction,
    type: 'application',
  },
  ar3_ApplicationInterface: {
    icon: ar3Interface,
    type: 'application',
  },
  ar3_ApplicationProcess: {
    icon: ar3Process,
    type: 'application',
  },
  ar3_ApplicationService: {
    icon: ar3Service,
    type: 'application',
  },
  ar3_ArchiDiagramModelReference: {
    icon: ar3ArchiDiagramModelReference,
    type: 'link',
  },
  ar3_Artifact: {
    icon: ar3Artifact,
    type: 'technology',
  },
  ar3_Assessment: {
    icon: ar3Assessment,
    type: 'motivation',
  },
  ar3_BusinessActor: {
    icon: ar3Actor,
    type: 'business',
  },
  ar3_BusinessCollaboration: {
    icon: ar3Collaboration,
    type: 'business',
  },
  ar3_BusinessEvent: {
    icon: ar3Event,
    type: 'business',
  },
  ar3_BusinessFunction: {
    icon: ar3Function,
    type: 'business',
  },
  ar3_BusinessInteraction: {
    icon: ar3Interaction,
    type: 'business',
  },
  ar3_BusinessInterface: {
    icon: ar3Interface,
    type: 'business',
  },
  ar3_BusinessObject: {
    icon: ar3Object,
    type: 'business',
  },
  ar3_BusinessProcess: {
    icon: ar3Process,
    type: 'business',
  },
  ar3_BusinessRole: {
    icon: ar3Role,
    type: 'business',
  },
  ar3_BusinessService: {
    icon: ar3Service,
    type: 'business',
  },
  ar3_Capability: {
    icon: ar3Capability,
    type: 'strategy',
  },
  ar3_CommunicationNetwork: {
    icon: ar3CommunicationNetwork,
    type: 'technology',
  },
  ar3_Constraint: {
    icon: ar3Constraint,
    type: 'motivation',
  },
  ar3_Contract: {
    icon: ar3Contract,
    type: 'business',
  },
  ar3_CourseOfAction: {
    icon: ar3CourseOfAction,
    type: 'strategy',
  },
  ar3_DataObject: {
    icon: ar3Object,
    type: 'application',
  },
  ar3_Deliverable: {
    icon: ar3Deliverable,
    type: 'implementation & migration',
  },
  ar3_Device: {
    icon: ar3Device,
    type: 'technology',
  },
  ar3_DistributionNetwork: {
    icon: ar3DistributionNetwork,
    type: 'physical',
  },
  ar3_Driver: {
    icon: ar3Driver,
    type: 'motivation',
  },
  ar3_Equipment: {
    icon: ar3Equipment,
    type: 'physical',
  },
  ar3_Facility: {
    icon: ar3Facility,
    type: 'physical',
  },
  ar3_Gap: {
    icon: ar3Gap,
    type: 'implementation & migration',
  },
  ar3_Goal: {
    icon: ar3Goal,
    type: 'motivation',
  },
  ar3_Grouping: {
    icon: ar3Grouping,
    type: 'composite',
  },
  ar3_ImplementationEvent: {
    icon: ar3Event,
    type: 'implementation & migration',
  },
  ar3_Location: {
    icon: ar3Location,
    type: 'location',
  },
  ar3_Material: {
    icon: ar3Material,
    type: 'physical',
  },
  ar3_Meaning: {
    icon: ar3Meaning,
    type: 'motivation',
  },
  ar3_Node: {
    icon: ar3Node,
    type: 'technology',
  },
  ar3_OrJunction: {
    icon: ar3Junction,
    type: 'or',
  },
  ar3_Outcome: {
    icon: ar3Outcome,
    type: 'motivation',
  },
  ar3_Path: {
    icon: ar3Path,
    type: 'technology',
  },
  ar3_Plateau: {
    icon: ar3Plateau,
    type: 'implementation & migration',
  },
  ar3_Principle: {
    icon: ar3Principle,
    type: 'motivation',
  },
  ar3_Product: {
    icon: ar3Product,
    type: 'business',
  },
  ar3_Representation: {
    icon: ar3Representation,
    type: 'business',
  },
  ar3_Requirement: {
    icon: ar3Requirement,
    type: 'motivation',
  },
  ar3_Resource: {
    icon: ar3Resource,
    type: 'strategy',
  },
  ar3_Stakeholder: {
    icon: ar3Role,
    type: 'motivation',
  },
  ar3_SystemSoftware: {
    icon: ar3SystemSoftware,
    type: 'technology',
  },
  ar3_TechnologyCollaboration: {
    icon: ar3Collaboration,
    type: 'technology',
  },
  ar3_TechnologyEvent: {
    icon: ar3Event,
    type: 'technology',
  },
  ar3_TechnologyFunction: {
    icon: ar3Function,
    type: 'technology',
  },
  ar3_TechnologyInteraction: {
    icon: ar3Interaction,
    type: 'technology',
  },
  ar3_TechnologyInterface: {
    icon: ar3Interface,
    type: 'technology',
  },
  ar3_TechnologyProcess: {
    icon: ar3Process,
    type: 'technology',
  },

  ar3_TechnologyService: {
    icon: ar3Service,
    type: 'technology',
  },
  ar3_Value: {
    icon: ar3Value,
    type: 'motivation',
  },
  ar3_ValueStream: {
    icon: ar3ValueStream,
    type: 'strategy',
  },
  ar3_WorkPackage: {
    icon: ar3WorkPackage,
    type: 'implementation & migration',
  },
  lineage_dataset: {
    icon: lineage_dataset,
    type: 'dataset',
  },
  lineage_process: {
    icon: lineage_process,
    type: 'process',
  },
};
