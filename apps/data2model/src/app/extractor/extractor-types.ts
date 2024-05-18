import { Dictionary } from 'lodash';

export type ExtractorDatasetEntry = Dictionary<any>;

export enum DefinitionType {
  ELEMENT = 'element',
  RELATION = 'relation',
  VIEW = 'view'
}
export enum ViewLayout {
  ARCHIMATE_HIERARCHICAL = 'archimate_hierarchical',
  ARCHIMATE_PROCESS = 'archimate_process',
  MANUAL = 'manual'
}
interface AttributeMapping {
  readonly key: string;
  readonly value: string;
}
interface StaticIdentifier {
  readonly id_type: 'static';
  readonly id_value: string;
}
interface DynamicIdentifier {
  readonly id_type: 'dynamic';
  readonly id_key: string;
  readonly id_prefix?: string;
}
interface AbstractDefinition {
  readonly id?: string;
  readonly type: DefinitionType;
  readonly suggestion_id?: string;
  readonly alias?: string;
  readonly description?: string;
  readonly include?: boolean;
  readonly mapping?: AttributeMapping[];
}
type BaseDefinition = (StaticIdentifier | DynamicIdentifier) &
  AbstractDefinition;
interface ElementBase {
  readonly type: DefinitionType.ELEMENT;
  readonly concept_type: string;
  readonly concept_name_key?: string;
  readonly concept_name_prefix?: string;
  readonly concept_label_key?: string;
  readonly concept_label_prefix?: string;
  readonly reversed?: boolean;
}
export type ElementDefinition = BaseDefinition & ElementBase;
interface RelationshipBase {
  readonly type: DefinitionType.RELATION;
  readonly source: string;
  readonly target: string;
  readonly relationship_type: string;
  readonly relationship_name_key?: string;
  readonly relationship_name_prefix?: string;
  readonly realationship_label_key?: string;
  readonly realationship_label_prefix?: string;
  readonly reversed?: boolean;
}
export type RelationshipDefinition = BaseDefinition & RelationshipBase;
interface StaticViewPath {
  readonly type: 'static';
  readonly value: string;
}
interface DynamicViewPath {
  readonly type: 'dynamic';
  readonly value: string;
  readonly prefix?: string;
}
type ViewPath = StaticViewPath | DynamicViewPath;
interface ViewNode {
  readonly rule: string;
}
interface ViewEdge {
  readonly rule: string;
}
interface StaticViewName {
  readonly view_name_type: 'static';
  readonly view_name_value: string;
}
interface DynamicViewName {
  readonly view_name_type: 'dynamic';
  readonly view_name_key: string;
  readonly view_name_prefix?: string;
}
type ViewName = StaticViewName | DynamicViewName;
interface ViewContent {
  readonly type: DefinitionType.VIEW;
  readonly view_path?: ViewPath[];
  readonly view_nodes?: ViewNode[];
  readonly view_edges?: ViewEdge[];
  readonly view_layout: ViewLayout;
}
export type ViewDefinition = BaseDefinition & ViewName & ViewContent;
export type ExtractorRule =
  | ElementDefinition
  | RelationshipDefinition
  | ViewDefinition;
export interface RulesContext {
  readonly name?: string;
  readonly rules?: Dictionary<ExtractorRule>;
}
export interface ModelCommitContext {
  readonly projectName: string;
  readonly branchName: string;
  readonly comment: string;
  readonly conflictResolutionTemplate: ConflictResolutionTemplateEnum;
}
export enum SaveAction {
  SAVE = 'save',
  SAVE_AS = 'saveAs'
}

export interface SuggestedRelation<T = Dictionary<any>> {
  id: string;
  source: keyof T;
  target: keyof T;
  rank: number;
  type: 'dynamic' | 'structural' | 'other';
  correlation: number;
  f1: number;
  referenceConsistency: number;
  reverseConsistency: number;
  sourceWordCount: number;
  targetWordCount: number;
  transitionEntropy: number;
}

export interface SuggestedColumn<T = Dictionary<any>> {
  column: keyof T;
  entropy: number;
}

export interface Suggestions<T = Dictionary<any>> {
  columns: SuggestedColumn<T>[];
  labels: SuggestedColumn<T>[];
  relations: Dictionary<SuggestedRelation<T>>;
}

export enum ConflictResolutionTemplateEnum {
  MANUAL = 'manual',
  REPOSITORY_ONLY = 'repository_only',
  UPLOAD_ONLY = 'upload_only',
  UNION_REPOSITORY = 'union_repository',
  UNION_UPLOAD = 'union_upload'
}

export enum ExtractorWorkerTask {
  SUGGESTIONS = 'suggestions',
  BIJACENCY_MAP = 'bijacency-map'
}

export interface ExtractorWorkerContext {
  task: ExtractorWorkerTask;
  context: Dictionary<any>;
}

export interface ValidationResult {
  readonly type: ValidationSeverityType;
  readonly rule: string;
  readonly description?: string;
}

export enum ValidationSeverityType {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error'
}
