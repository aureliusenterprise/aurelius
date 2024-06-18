export interface CanonicalView {
  readonly id: string;
  readonly name: string;
  readonly path: string;
  readonly props: any[];
  readonly docs: string;
  readonly dttm: number;
  readonly json: CanonicalViewJson;
}

export interface CanonicalViewJson {
  readonly nodes: CanonicalNode[];
  readonly relations: CanonicalRelation[];
}

export interface CanonicalNodeStyle {
  readonly border_type?: string;
  readonly fill_color?: string;
  readonly font_color?: string;
  readonly font_name?: string;
  readonly font_size?: number;
  readonly text_alignment?: string;
  readonly text_position?: string;
}

export interface CanonicalNode {
  readonly id: string;
  readonly branch: string;
  readonly concept_type: string;
  readonly height: number;
  readonly language_version: string;
  readonly revision: number;
  readonly style: CanonicalNodeStyle;
  readonly width: number;
  readonly view_ref: string;
  readonly x: number;
  readonly y: number;
  readonly node_identifier?: string;
  readonly name?: string;
}

export interface CanonicalRelationBendpoint {
  readonly x: number;
  readonly y: number;
}

export interface CanonicalRelationStyle {
  readonly lineColor?: string;
}

export interface CanonicalRelation {
  readonly id: string;
  readonly bendpoints: CanonicalRelationBendpoint[];
  readonly branch: string;
  readonly language_version: string;
  readonly revision: number;
  readonly source: string;
  readonly style: CanonicalRelationStyle;
  readonly target: string;
  readonly type: string;
  readonly name?: string;
  readonly relation_identifier?: string;
}
