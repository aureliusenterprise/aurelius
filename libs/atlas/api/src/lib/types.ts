import { Dictionary } from 'lodash';

export interface GetOptions {
  /** Whether or not to refresh the cache */
  readonly forceUpdate?: boolean;
}

export interface ListOfDomainsForDashboard {
  totalNumberOfDomains: number;
  totalNumberOfActiveDomains: number;
  domains: ListOfDomains;
}
export interface ListOfDomains {
  CM: DomainForDashboard;
  Communication: DomainForDashboard;
  'Executive Commitee': DomainForDashboard;
  'Engineering & Estimating': DomainForDashboard;
  'Finance and Control': DomainForDashboard;
  'Facility Services': DomainForDashboard;
  IT: DomainForDashboard;
  'Legal Department': DomainForDashboard;
  MNGT: DomainForDashboard;
  'Personel and Organization': DomainForDashboard;
  'Project Office': DomainForDashboard;
  QHSE: DomainForDashboard;
  QPS: DomainForDashboard;
  'Ship Management Department': DomainForDashboard;
  STM: DomainForDashboard;
  Survey: DomainForDashboard;
  Treasury: DomainForDashboard;
  Subsidiaries: DomainForDashboard;
  'Procurement & Supply Chain': DomainForDashboard;
}

export interface DomainForDashboard {
  name: string;
  guid: string;
  isActive: boolean;
  totalNumberOfEntities: number;
}
export interface Facet {
  readonly type: string;
}

export interface FilterEntity {
  readonly guid: FilterResult;
  readonly name: string;
}

export interface FilterChoice {
  readonly valueGuid?: string;
  readonly valueName?: string;
  readonly valueCount?: number;
  readonly option?: string;
}
export interface FacetData {
  readonly value: string;
  readonly count: number;
}
export interface Facet {
  readonly type: string;
  readonly size: number;
  readonly data?: Array<FacetData>;
}

export interface Field {
  readonly raw?: object;
  readonly snippet?: object;
}

export interface FilterValuesByFieldName {
  [fieldName: string]: string[];
}

export type SortingDirection = 'asc' | 'desc';

export interface SortingDirectionByFieldName {
  [fieldName: string]: SortingDirection;
}

export interface FiltersInOrder {
  attributes: Array<Facet>;
  name: string;
  whiteList: PropertiesForOrderList;
}

export type Facets = Dictionary<Facet>;

export interface ElasticSearchResults {
  readonly meta?: Meta;
  readonly results?: Array<ElasticSearchResult>;
  readonly facets?: Facets;
}

export interface ConfigurationForOrderList {
  supertypenames: PropertiesForOrderList;
  deriveddatadomain: PropertiesForOrderList;
  deriveddataentity: PropertiesForOrderList;
  derivedsystem: PropertiesForOrderList;
  derivedcollection: PropertiesForOrderList;
  deriveddataset: PropertiesForOrderList;
  classificationtext: PropertiesForOrderList;
  derivedperson: PropertiesForOrderList;
  sourcetype: PropertiesForOrderList;
  datadomainname: PropertiesForOrderList;
  dataqualityruledimension: PropertiesForOrderList;
}

export interface PropertiesForWhiteList {
  cardinalitySET: boolean;
  description: string;
  isReference: boolean;
  showIfEmpty: boolean;
}
export interface PropertiesForOrderList {
  typeList: string;
  condicional: boolean;
  position: number;
  hasAnyOption: boolean;
  excludeSubTypeBox: boolean;
}

export interface AtlasSearchResult {
  approximateCount: number;
  attributes: AtlasSearchResultAttributes;
  classification: string;
  entities: EntityElement[];
  fullTextResult: FullTextResult[];
  nextMarker: string;
  queryText: string;
  queryType: string;
  referredEntities: ReferredEntities;
  searchParameters: SearchParameters;
  type: string;
}

export interface AtlasSearchResultAttributes {
  name: string[];
  values: Array<Value[]>;
}

export interface FullTextResult {
  entity: FullTextResultEntity;
  score: number;
}

export interface FullTextResultEntity {
  classificationNames: string[];
  classifications: Value[];
  displayText: string;
  guid: string;
  isIncomplete: boolean;
  labels: string[];
  meaningNames: string[];
  meanings: Value[];
  status: string;
  attributes: EntityAttributes;
  typeName: string;
}

export interface ReferredEntities {
  [guid: string]: EntityElement;
}

export interface SearchParameters {
  attributes: string[];
  classification: string;
  entityFilters: Filters;
  excludeDeletedEntities: boolean;
  includeClassificationAttributes: boolean;
  includeSubClassifications: boolean;
  includeSubTypes: boolean;
  limit: number;
  marker: string;
  offset: number;
  query: string;
  sortBy: string;
  sortOrder: string;
  tagFilters: Filters;
  termName: string;
  typeName: string;
}
export interface Filters {
  attributeName: string;
  attributeValue: string;
  condition: string;
  criterion: Value[];
  operator: string;
}

export interface FiltersFromBackend {
  meta: Meta;
  results: Array<ElasticSearchResult>;
}

export interface ElasticSearchResult {
  guid: FilterResult;
  id: FilterResult;
  [field: string]: FilterResult;
}

export interface FilterResult {
  raw: any;
  snippet?: string;
}

export interface Meta {
  alerts: Array<any>;
  engine: Engine;
  page: Page;
  warnings: Array<any>;
  precision: number;
  request_id: string;
}
export interface Page {
  current: number;
  size: number;
  total_pages: number;
  total_results: number;
}
export interface Engine {
  name: string;
  type: string;
}
export interface Classification {
  entityGuid: string;
  entityStatus: string;
  propagate: boolean;
  removePropagationsOnEntityDelete: boolean;
  validityPeriods?: Value[];
  attributes?: EntityAttributes;
  typeName: string;
}

export type Value = any;

export interface EntityAttributes {
  [key: string]: Value;
}

export interface EntityElement {
  attributes: EntityAttributes;
  guid: string;
  typeName: string;
  classifications: Classification[];
  classificationNames?: string[];
  displayText?: string;
  isIncomplete?: boolean;
  labels?: string[];
  meaningNames?: string[];
  meanings?: Meaning[];
  status?: string;
}

export interface Meaning {
  confidence: number;
  createdBy: string;
  description: string;
  displayText: string;
  expression: string;
  relationGuid: string;
  source: string;
  status: string;
  steward: string;
  termGuid: string;
}

export interface ClassificationResponse {
  businessMetadataDefs: Array<AtlasEntityDef>;
  classificationDefs: Array<AtlasEntityDef>;
  entityDefs: Array<AtlasEntityDef>;
  enumDefs: Array<AtlasEntityDef>;
  relationshipDefs: Array<AtlasEntityDef>;
  structDefs: Array<AtlasEntityDef>;
}

export interface Term {
  description?: string;
  name?: string;
}
export interface ClassificationTag {
  [key: number]: ClassificationItem;
}

export interface ClassificationItem {
  [key: number]: string;
}
export interface TermDetails {
  anchor: TermAnchor;
  assignedEntities: Array<AssignedEntity>;
  categories: Array<Category>;
  glossaryTermHeader: GlossaryTermHeader;
  guid: string;
  name: string;
  qualifiedName: string;
  longDescription: string;
  shortDescription: string;
}
export interface Category {
  categoryGuid: string;
  displayText: string;
  relationGuid: string;
}
export interface GlossaryTermHeader {
  qualifiedName: string;
  termGuid: string;
}

export interface AssignedEntity {
  displayText: string;
  entityStatus: string;
  guid: string;
  relationshipAttributes: RelationshipAttribute;
  relationshipGuid: string;
  relationshipStatus: string;
  relationshipType: string;
  typeName: string;
}
export interface RelationshipAttribute {
  attributes?: Attributes;
  typeName: string;
}
export interface Attributes {
  confidence: string;
  createdBy: string;
  description: string;
  expression: string;
  source: string;
  status: string;
  steward: string;
}

export interface TermAnchor {
  glossaryGuid: string;
  relationGuid: string;
}

export interface EntityMutationResponse {
  guidAssignments: GUIDAssignments;
  mutatedEntities: MutatedEntities;
  partialUpdatedEntities: AtlasEntityHeader[];
}

export interface GUIDAssignments {
  [property: string]: string;
}

export interface MutatedEntities {
  [property: string]: AtlasEntityHeader[];
}

export interface AtlasEntityHeader {
  classificationNames: string[];
  classifications: Classification[];
  displayText: string;
  guid: string;
  isIncomplete: boolean;
  labels: string[];
  meaningNames: string[];
  meanings: Meaning[];
  status: 'ACTIVE' | 'DELETED' | 'PURGED';
  attributes: Attributes;
  typeName: string;
}

export interface AtlasEntityWithEXTInformation {
  entity: EntityElementWithEXTInfo;
  referredEntities: ReferredEntities;
}

export interface EntityElementWithEXTInfo extends EntityElement {
  relationshipAttributes: EntityAttributes;
  businessAttributes?: EntityAttributes;
  customAttributes?: EntityAttributes;
  createTime?: number;
  createdBy?: string;
  homeId?: string;
  pendingTasks?: string[];
  provenanceType?: number;
  proxy?: boolean;
  updateTime?: number;
  updatedBy?: string;
  version?: number;
}

export interface AtlasTypesDef {
  readonly businessMetadataDefs: StructDef[];
  readonly classificationDefs: ClassificationDef[];
  readonly entityDefs: AtlasEntityDef[];
  readonly enumDefs: EnumDef[];
  readonly relationshipDefs: RelationshipDef[];
  readonly structDefs: StructDef[];
}

export interface BaseTypeDef {
  readonly category: string;
  readonly createTime: number;
  readonly createdBy: string;
  readonly dateFormatter: DateFormat;
  readonly description: string;
  readonly guid: string;
  readonly name: string;
  readonly options: Options;
  readonly serviceType: string;
  readonly typeVersion: string;
  readonly updateTime: number;
  readonly updatedBy: string;
  readonly version: number;
}

export interface StructDef extends BaseTypeDef {
  readonly attributeDefs: AttributeDef[];
}

export interface ClassificationDef extends StructDef {
  readonly entityTypes: string[];
  readonly subTypes: string[];
  readonly superTypes: string[];
}

export interface AtlasEntityDef extends StructDef {
  readonly businessAttributeDefs: BusinessAttributeDefs;
  readonly relationshipAttributeDefs: AttributeDef[];
  readonly subTypes: string[];
  readonly superTypes: string[];
}

export interface EnumDef extends BaseTypeDef {
  readonly defaultValue: string;
  readonly elementDefs: EnumElementDef;
}

export interface EnumElementDef {
  readonly description: string;
  readonly ordinal: number;
  readonly value: string;
}

export interface RelationshipDef extends StructDef {
  readonly endDef1: RelationshipEndDef;
  readonly endDef2: RelationshipEndDef;
  readonly propagateTags: string;
  readonly relationshipCategory: string;
  readonly relationshipLabel: string;
}

export interface AttributeDef {
  readonly cardinality: Cardinality;
  readonly constraints: ConstraintDef[];
  readonly defaultValue: string;
  readonly description: string;
  readonly displayName: string;
  readonly includeInNotification: boolean;
  readonly indexType: IndexType;
  readonly isIndexable: boolean;
  readonly isOptional: boolean;
  readonly isUnique: boolean;
  readonly name: string;
  readonly options: Options;
  readonly searchWeight: number;
  readonly typeName: string;
  readonly valuesMaxCount: number;
  readonly valuesMinCount: number;
  readonly isLegacyAttribute?: boolean;
  readonly relationshipTypeName?: string;
}

export interface ConstraintDef {
  readonly params: { [key: string]: object };
  readonly type: string;
}

export enum Cardinality {
  List = 'LIST',
  Set = 'SET',
  Single = 'SINGLE',
}

export enum IndexType {
  Default = 'DEFAULT',
  String = 'STRING',
}

export interface Options {
  readonly [property: string]: string;
}

export interface BusinessAttributeDefs {
  readonly [property: string]: AttributeDef[];
}

export interface DateFormat {
  readonly availableLocales: string[];
  readonly calendar: number;
  readonly lenient: boolean;
  readonly dateInstance?: DateFormat;
  readonly dateTimeInstance?: DateFormat;
  readonly instance?: DateFormat;
  readonly numberFormat?: DateFormat;
  readonly timeInstance?: DateFormat;
  readonly timeZone?: DateFormat;
}

export interface RelationshipEndDef {
  readonly cardinality: Cardinality;
  readonly description: string;
  readonly isContainer: boolean;
  readonly isLegacyAttribute: boolean;
  readonly name: string;
  readonly type: string;
}
