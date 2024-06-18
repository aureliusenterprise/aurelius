import { Dictionary } from 'lodash';

export type ModelProperties = Dictionary<any>;

export type ParserType =
  | 'element'
  | 'relationship'
  | 'view'
  | 'node'
  | 'connection';

export type ModelEntity =
  | ModelElement
  | ModelRelation
  | ModelView
  | ModelViewNode
  | ModelViewConnection;

export interface ModelInfo {
  readonly name?: string;
}

export interface BaseModelEntity {
  readonly id: string;
  readonly parserType: ParserType;
  readonly type: string;
  readonly displayName?: string;
  readonly humanReadableType?: string;
  readonly name?: string;
}

export interface ModelElement extends BaseModelEntity {
  readonly parserType: 'element';
  readonly properties: ModelProperties;
  readonly description?: string;
}

export type ModelRelationOptions = Dictionary<any>;

export interface ModelRelation extends BaseModelEntity {
  readonly options: ModelRelationOptions;
  readonly parserType: 'relationship';
  readonly properties: ModelProperties;
  readonly source: string;
  readonly target: string;
  readonly description?: string;
}

export type ModelViewNodeTextAlignment = 'center' | 'left' | 'right';

export type ModelViewNodeTextPosition = 'top' | 'middle' | 'bottom';

export interface ModelViewNodeStyle {
  readonly borderType?: number;
  readonly fillColor?: string;
  readonly fontColor?: string;
  readonly fontName?: string;
  readonly fontSize?: string;
  readonly textAlignment?: ModelViewNodeTextAlignment;
  readonly textPosition?: ModelViewNodeTextPosition;
}

export interface ModelViewNode extends BaseModelEntity {
  readonly height: number;
  readonly parserType: 'node';
  readonly style: ModelViewNodeStyle;
  readonly width: number;
  readonly x: number;
  readonly y: number;
  readonly ref?: string;
}

export interface ModelViewConnectionBendpoint {
  readonly x: number;
  readonly y: number;
}

export interface ModelViewConnectionStyle {
  readonly lineColor?: string;
}

export interface ModelViewConnection extends BaseModelEntity {
  readonly bendpoints: ModelViewConnectionBendpoint[];
  readonly parserType: 'connection';
  readonly source: string;
  readonly style: ModelViewConnectionStyle;
  readonly target: string;
  readonly ref?: string;
}

export interface ModelView extends BaseModelEntity {
  readonly connections: Dictionary<ModelViewConnection>;
  readonly nodes: Dictionary<ModelViewNode>;
  readonly parserType: 'view';
  readonly properties: ModelProperties;
  readonly description?: string;
}

export interface ModelParserResult {
  readonly elements: Dictionary<ModelElement>;
  readonly info: ModelInfo;
  readonly organizations: Dictionary<string>;
  readonly relations: Dictionary<ModelRelation>;
  readonly views: Dictionary<ModelView>;
}

export type ModelParserFunction = (
  jsonModel: any
) => Promise<ModelParserResult>;
