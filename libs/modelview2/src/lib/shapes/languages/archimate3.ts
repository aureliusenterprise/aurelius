import { archimate3 as meta } from '@models4insight/metamodel';
import { BasicShapeFunction, basicShapes, compose } from '../basic-shapes';
import {
  ConnectionStyleFunction,
  NodeShapeFunction,
  RelationDef,
} from '../types';

const grouping: BasicShapeFunction = (width, height) => {
  const titleBlock = `m0,0h${width / 2}v18h-${width / 2}z`;

  const mainBlock = `m0,18h${width}v${height - 18}h-${width}z`;

  return titleBlock + mainBlock;
};

const wavedRectangle: BasicShapeFunction = (width, height) =>
  `m0,0v${height - 6}q${width / 4},12,${width / 2},0t${width / 2},0v-${
    height - 6
  }z`;

export const ar3Classes: {
  [key in keyof typeof meta.elements]?: string;
} = {
  ar3_AndJunction: 'and',
  ar3_ApplicationCollaboration: 'application',
  ar3_ApplicationComponent: 'application',
  ar3_ApplicationEvent: 'application',
  ar3_ApplicationFunction: 'application',
  ar3_ApplicationInteraction: 'application',
  ar3_ApplicationInterface: 'application',
  ar3_ApplicationProcess: 'application',
  ar3_ApplicationService: 'application',
  ar3_Artifact: 'technology',
  ar3_Assessment: 'motivation',
  ar3_BusinessActor: 'business',
  ar3_BusinessCollaboration: 'business',
  ar3_BusinessEvent: 'business',
  ar3_BusinessFunction: 'business',
  ar3_BusinessInteraction: 'business',
  ar3_BusinessInterface: 'business',
  ar3_BusinessObject: 'business',
  ar3_BusinessProcess: 'business',
  ar3_BusinessRole: 'business',
  ar3_BusinessService: 'business',
  ar3_Capability: 'strategy',
  ar3_CommunicationNetwork: 'technology',
  ar3_Constraint: 'motivation',
  ar3_Contract: 'business',
  ar3_CourseOfAction: 'strategy',
  ar3_DataObject: 'application',
  ar3_Deliverable: 'technology',
  ar3_Device: 'technology',
  ar3_DistributionNetwork: 'physical',
  ar3_Driver: 'motivation',
  ar3_Equipment: 'physical',
  ar3_Facility: 'physical',
  ar3_Gap: 'implementation & migration',
  ar3_Goal: 'motivation',
  ar3_Grouping: 'composite',
  ar3_ImplementationEvent: 'implementation & migration',
  ar3_Location: 'location',
  ar3_Material: 'physical',
  ar3_Meaning: 'motivation',
  ar3_Node: 'technology',
  ar3_OrJunction: 'or',
  ar3_Outcome: 'motivation',
  ar3_Path: 'technology',
  ar3_Plateau: 'implementation & migration',
  ar3_Principle: 'motivation',
  ar3_Product: 'business',
  ar3_Representation: 'business',
  ar3_Requirement: 'motivation',
  ar3_Resource: 'strategy',
  ar3_Stakeholder: 'motivation',
  ar3_SystemSoftware: 'technology',
  ar3_TechnologyCollaboration: 'technology',
  ar3_TechnologyEvent: 'technology',
  ar3_TechnologyFunction: 'technology',
  ar3_TechnologyInteraction: 'technology',
  ar3_TechnologyInterface: 'technology',
  ar3_TechnologyProcess: 'technology',
  ar3_TechnologyService: 'technology',
  ar3_Value: 'motivation',
  ar3_ValueStream: 'strategy',
  ar3_WorkPackage: 'implementation & migration',
  ar3_Unknown: 'unknown',
};

export const ar3Elements: {
  [key in keyof typeof meta.elements]?: NodeShapeFunction;
} = {
  ar3_AndJunction: compose(basicShapes.ellipse, {
    showIcon: false,
    showName: false,
  }),
  ar3_ApplicationCollaboration: compose(basicShapes.roundedRectangle),
  ar3_ApplicationComponent: compose(basicShapes.rectangle),
  ar3_ApplicationEvent: compose(basicShapes.roundedRectangle),
  ar3_ApplicationFunction: compose(basicShapes.roundedRectangle),
  ar3_ApplicationInteraction: compose(basicShapes.rectangle),
  ar3_ApplicationInterface: compose(basicShapes.rectangle),
  ar3_ApplicationProcess: compose(basicShapes.roundedRectangle),
  ar3_ApplicationService: compose(basicShapes.roundedRectangle),
  ar3_Artifact: compose(basicShapes.rectangle),
  ar3_Assessment: compose(basicShapes.octagon),
  ar3_BusinessActor: compose(basicShapes.rectangle),
  ar3_BusinessCollaboration: compose(basicShapes.roundedRectangle),
  ar3_BusinessEvent: compose(basicShapes.roundedRectangle),
  ar3_BusinessFunction: compose(basicShapes.roundedRectangle),
  ar3_BusinessInteraction: compose(basicShapes.roundedRectangle),
  ar3_BusinessInterface: compose(basicShapes.rectangle),
  ar3_BusinessObject: compose(basicShapes.rectangle),
  ar3_BusinessProcess: compose(basicShapes.roundedRectangle),
  ar3_BusinessRole: compose(basicShapes.rectangle),
  ar3_BusinessService: compose(basicShapes.roundedRectangle),
  ar3_Capability: compose(basicShapes.roundedRectangle),
  ar3_CommunicationNetwork: compose(basicShapes.rectangle),
  ar3_Constraint: compose(basicShapes.octagon),
  ar3_Contract: compose(basicShapes.rectangle),
  ar3_CourseOfAction: compose(basicShapes.roundedRectangle),
  ar3_DataObject: compose(basicShapes.rectangle),
  ar3_Deliverable: compose(wavedRectangle),
  ar3_Device: compose(basicShapes.rectangle),
  ar3_DistributionNetwork: compose(basicShapes.rectangle),
  ar3_Driver: compose(basicShapes.octagon),
  ar3_Equipment: compose(basicShapes.rectangle),
  ar3_Facility: compose(basicShapes.rectangle),
  ar3_Gap: compose(basicShapes.rectangle),
  ar3_Goal: compose(basicShapes.octagon),
  ar3_Grouping: compose(grouping, { showIcon: false }),
  ar3_ImplementationEvent: compose(basicShapes.roundedRectangle),
  ar3_Location: compose(basicShapes.rectangle),
  ar3_Material: compose(basicShapes.rectangle),
  ar3_Meaning: compose(basicShapes.octagon),
  ar3_Node: compose(basicShapes.rectangle),
  ar3_OrJunction: compose(basicShapes.ellipse, {
    showIcon: false,
    showName: false,
  }),
  ar3_Outcome: compose(basicShapes.octagon),
  ar3_Path: compose(basicShapes.rectangle),
  ar3_Plateau: compose(basicShapes.rectangle),
  ar3_Principle: compose(basicShapes.octagon),
  ar3_Product: compose(basicShapes.rectangle),
  ar3_Representation: compose(wavedRectangle),
  ar3_Requirement: compose(basicShapes.octagon),
  ar3_Resource: compose(basicShapes.rectangle),
  ar3_Stakeholder: compose(basicShapes.octagon),
  ar3_SystemSoftware: compose(basicShapes.rectangle),
  ar3_TechnologyCollaboration: compose(basicShapes.roundedRectangle),
  ar3_TechnologyEvent: compose(basicShapes.roundedRectangle),
  ar3_TechnologyFunction: compose(basicShapes.roundedRectangle),
  ar3_TechnologyInteraction: compose(basicShapes.roundedRectangle),
  ar3_TechnologyInterface: compose(basicShapes.rectangle),
  ar3_TechnologyProcess: compose(basicShapes.roundedRectangle),
  ar3_TechnologyService: compose(basicShapes.roundedRectangle),
  ar3_Unknown: compose(basicShapes.rectangle),
  ar3_Value: compose(basicShapes.ellipse),
  ar3_ValueStream: compose(basicShapes.roundedRectangle),
  ar3_WorkPackage: compose(basicShapes.roundedRectangle),
};

const access: ConnectionStyleFunction = (_, relation) => {
  return {
    'marker-start': ['Read', 'ReadWrite'].includes(relation.options.accessType)
      ? 'access-read'
      : null,
    'marker-end': ['Write', 'ReadWrite'].includes(relation.options.accessType)
      ? 'generic-arrow-open'
      : null,
    'stroke-dasharray': '2,2',
  };
};

const association: ConnectionStyleFunction = (_, relation) => {
  return {
    'marker-end': relation.options.isDirected ? 'association' : null,
  };
};

export const ar3RelationDef: { [key: string]: RelationDef } = {
  'access-read': {
    refX: 0,
    refY: 3,
    markerWidth: 6,
    markerHeight: 7,
    path: 'M7,0l-7,3l7,3',
    fill: 'none',
    stroke: '#000000',
  },
  aggregation: {
    refX: 0,
    refY: 6,
    markerWidth: 20,
    markerHeight: 12,
    path: 'M10,0l10,6l-10,6l-10,-6l10,-6z',
    fill: '#FFFFFF',
    stroke: '#000000',
  },
  'assignment-start': {
    refX: 0,
    refY: 3,
    markerWidth: 6,
    markerHeight: 6,
    path: 'M0,0a3,3,0,0,0,6,6a3,3,0,0,0,-6,-6z',
    fill: '#000000',
  },
  association: {
    refX: 10,
    refY: 6,
    markerWidth: 10,
    markerHeight: 10,
    path: 'M0,0L10,6',
    fill: 'none',
    stroke: '#000000',
  },
  'block-arrow': {
    refX: 10,
    refY: 7,
    markerWidth: 10,
    markerHeight: 14,
    path: 'M0,0v14l10,-7z',
    fill: '#FFFFFF',
    stroke: '#000000',
  },
  composition: {
    refX: 0,
    refY: 6,
    markerWidth: 20,
    markerHeight: 12,
    path: 'M10,0l10,6l-10,6l-10,-6l10,-6z',
    fill: '#000000',
  },
  'generic-arrow': {
    refX: 7,
    refY: 3,
    markerWidth: 6,
    markerHeight: 7,
    path: 'M0,0l7,3l-7,3z',
    fill: '#000000',
  },
  'generic-arrow-open': {
    refX: 7,
    refY: 3,
    markerWidth: 6,
    markerHeight: 7,
    path: 'M0,0l7,3l-7,3',
    fill: 'none',
    stroke: '#000000',
  },
};

export const ar3Relations: {
  [key in keyof typeof meta.relations_by_tag]?: ConnectionStyleFunction;
} = {
  ar3_Access: access,
  ar3_Aggregation: () => ({ 'marker-start': 'aggregation' }),
  ar3_Assignment: () => ({
    'marker-start': 'assignment-start',
    'marker-end': 'generic-arrow',
  }),
  ar3_Association: association,
  ar3_Composition: () => ({ 'marker-start': 'composition' }),
  ar3_Flow: () => ({
    'marker-end': 'generic-arrow',
    'stroke-dasharray': '4,2',
  }),
  ar3_Influence: () => ({
    'marker-end': 'generic-arrow-open',
    'stroke-dasharray': '4,2',
  }),
  ar3_Realization: () => ({
    'marker-end': 'block-arrow',
    'stroke-dasharray': '2,2',
  }),
  ar3_Serving: () => ({
    'marker-end': 'generic-arrow-open',
  }),
  ar3_Specialization: () => ({
    'marker-end': 'block-arrow',
  }),
  ar3_Triggering: () => ({
    'marker-end': 'generic-arrow',
  }),
};
