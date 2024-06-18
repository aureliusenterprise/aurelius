import {
  ModelElement,
  ModelRelation,
  ModelViewConnection,
  ModelViewNode,
} from '../parsers';

export interface NodeShapeDefinition {
  readonly shape: string;
  readonly showIcon?: boolean;
  readonly showName?: boolean;
}

export type NodeShapeFunction = (
  node: ModelViewNode,
  element?: ModelElement
) => NodeShapeDefinition;

export interface ConnectionStyleDescriptor {
  readonly 'marker-start'?: string;
  readonly 'marker-end'?: string;
  readonly 'stroke-dasharray'?: string;
}

export interface RelationDef {
  readonly refX: number;
  readonly refY: number;
  readonly markerWidth: number;
  readonly markerHeight: number;
  readonly path: string;
  readonly fill: string;
  readonly stroke?: string;
}

export type ConnectionStyleFunction = (
  connection: ModelViewConnection,
  relation?: ModelRelation
) => ConnectionStyleDescriptor;
