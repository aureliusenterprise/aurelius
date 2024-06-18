import { StoreSnapshot } from '@models4insight/redux';

export type ModelCompareDifferenceType =
  | 'added'
  | 'changed'
  | 'removed'
  | 'unchanged';

export interface ModelCompareDifference {
  readonly id: string;
  readonly difference: ModelCompareDifferenceType;
}

export interface ModelCompareResult {
  readonly model: any;
  readonly differences: ModelCompareDifference[];
}

/**
 * Represents repository version information
 */
export interface RepositoryVersion {
  /** The shortened git commit hash of the current repository version */
  readonly abbrev: string;
  /** The git branch name of the current repository version */
  readonly branch: string;
  /** The time at which the current version was built */
  readonly build_time: string;
  /** The full version string of the current repository version consisting of the release number and the git commit hash, delimited by a `#` sign */
  readonly version: string;
}

/**
 * Represents a specific concept that is exempt from a particular metric.
 */
export interface MetricExemption {
  /** The id of the exempt concept */
  readonly concept_id: string;
  /** The name of the metric from which the concept is exempt */
  readonly metric: string;
  /** The id of the project to which the concept belongs */
  readonly project_id: string;
  /** Specify the branch id if the exemption should only apply to a specific branch */
  readonly branch?: string;
  /** A description of why the concept is exempt */
  readonly comment?: string;
  /** The id of the metric exemption. Is set by the database */
  readonly id?: string;
  /** Specify the version timestamp if the exemption should only apply to a specific model version */
  readonly version?: number;
}

/**
 * Generic application permission levels.
 * Permissions form a hierarchy. The higher the number, the lower the permission level.
 * Permissions from lower levels apply to higher levels as well.
 */
export enum PermissionLevel {
  /** No permission required */
  UNRESTRICTED = -1,
  /** Can perform delete actions and assign other owners */
  OWNER = 0,
  /** Can alter properties and settings including access control */
  MAINTAINER = 1,
  /** Can commit changes to the model */
  CONTRIBUTOR = 2,
  /** Can retrieve models in Archi format */
  MODEL_USER = 3,
  /** Can use the model explorer and business dashboards */
  BUSINESS_USER = 4,
}

/** Additional permission levels for use with branch access control */
export enum BranchPermission {}

/** Additional permission levels for use with project access control */
export enum ProjectPermission {}

/** Permission levels for use with branch access control */
export type BranchPermissionLevel = PermissionLevel | BranchPermission;

/** Permission levels for use with project access control */
export type ProjectPermissionLevel = PermissionLevel | ProjectPermission;

export interface GetOptions {
  /** Whether or not to refresh the cache */
  readonly forceUpdate?: boolean;
}

export interface UserGroup {
  readonly id?: string;
  readonly project_id?: string;
  readonly name: string;
  readonly description: string;
  readonly members: string[];
}

export interface BranchMembers {
  [username: string]: BranchPermissionLevel;
}

export interface Branch {
  readonly id?: string;
  readonly description: string;
  readonly name: string;
  readonly project_id?: string;
  readonly protected?: boolean;
  readonly members: BranchMembers;
}

/**
 * Returned by the API for traceability of a branch move
 */
export interface BranchCommit {
  /** The name of the parser used for the operation */
  parserName: string;
  /** The full name of the project this operation relates to */
  projectName: string;
  /** The name of the source branch*/
  branchName: string;
  /** The comment supplied by the user for this operation */
  comment: string;
  /** The time at which this operation started */
  version: string;
  /** The username of the user who started this operation */
  userid: string;
  /** The ID of the operation assigned by the API */
  taskId: string;
  /** The name of the target branch */
  toBranch: string;
  /** The ID of the module this operation relates to */
  module?: string;
}

/**
 * Provides a summary of a branch for display in the UI
 */
export interface BranchSummary {
  /** The name of the branch */
  _id: string;
  /** The number of model versions in this branch */
  cnt: number;
  /** The timestamp at which this branch was created */
  min_start_date: { $numberLong: number };
  /** The latest provenance item for this branch*/
  last_update: ModelProvenance;
}

export enum ConflictResolutionTemplateEnum {
  MANUAL = 'manual',
  REPOSITORY_ONLY = 'repository_only',
  UPLOAD_ONLY = 'upload_only',
  UNION_REPOSITORY = 'union_repository',
  UNION_UPLOAD = 'union_upload',
}

/** Represents a conflict in the model */
export interface Conflict {
  /** Represents the current state of the repository */
  left?: ConflictSide;
  /** What changed in the repository */
  leftChange?: ConflictChangeTypeEnum;
  /** Represents the current state of the upload */
  right?: any;
  /** What changed in the uploaded model */
  rightChange?: ConflictChangeTypeEnum;
  /** The type of model element this conflict relates to */
  type?: ConflictTypeEnum;
  /** How this conflict was resolved by the user */
  resolution?: ConflictResolutionTemplateEnum;
}

/** All possible values of a conflict change type */
export enum ConflictChangeTypeEnum {
  UNCHANGED = 'unchanged',
  ADDED = 'added',
  DELETED = 'deleted',
  MODIFIED = 'modified',
}

export interface ConflictSide {
  /** The unprocessed raw conflicting item */
  raw: any;
  /** The path in the organization of the conflicting item */
  organization: ConflictSideOrganization[];
  /** The name of the conflicting item */
  name: string;
  /** The ID of the conflicting item */
  id: string;
  /** The hash of the conflicting item */
  hash: number;
  /** The type of the conflicting item */
  type: string;
  /** The full name of the project to which the conflicting item belongs */
  project: string;
  /** The name of the branch to which the conflicting item belongs */
  branch: string;
  /** The ID of the model to which the conflicting item belongs */
  model_id: string;
  /** The timestamp at which the conflicting item was added to the model */
  start_date: number;
  /** The timestamp at which the conflicting item expires or has expired */
  end_date2: number;
  /** Whether the conflicting item originates from the repository (left) or from the uploaded model (right) */
  source: 'left' | 'right';
}

export interface ConflictSideOrganization {
  /** The name of the subfolder */
  label: string;
  /** The index of the subfolder in the overall path */
  position: number;
}

/** All possible values of a conflict type */
export enum ConflictTypeEnum {
  NODES = 'nodes',
  RELATIONS = 'relations',
  VIEWS = 'views',
}

/** Request body for submitting an error to the API */
export class ErrorContext {
  /** The name of the application */
  app: string;
  /** The error as thrown */
  error: Error;
  /** The username of the current user */
  userid: string;
  /** A snapshot of the current application state */
  state?: StoreSnapshot;
  /** The current app version */
  version: string;
  /** The timestamp at which the error was recorded */
  created_at?: number;
}

/**
 * Returned by the API for traceability of a model commit
 */
export interface ModelCommit {
  /** The name of the parser used */
  parserName?: string;
  /** The full name of the project the model was committed to */
  projectName?: string;
  /** The name of the branch the model was committed to */
  branchName?: string;
  /** The ID of the module the model was committed to */
  module?: string;
  /** The ID of the committed model assigned by the API */
  modelId?: string;
  /** The content type of the model as it was committed */
  contentType?: ModelCommitContentTypeEnum;
  /** The comment provided by the user */
  comment?: string;
  /** The timestamp at which the model was committed */
  version?: string;
  /** The username of the user who committed the model */
  userid?: string;
  /** The ID of the commit operation assigned by the API */
  taskId?: string;
}

export enum ModelCommitContentTypeEnum {
  /** Archimate 3.0 */
  ARCHIMATE = 'archimate',
  /** XML */
  XML = 'xml',
  /** JSON */
  JSON = 'json',
}

/** Represents a single provenance item */
export interface ModelProvenance {
  /** ?? */
  name: string;
  /** The ID of this provenance item */
  id: string;
  /** The ID of the module this operation relates to */
  module: string;
  /** The ID of the model this operation relates to */
  modelId: string;
  /** The model type of the model this operation relates to */
  type: ParserNameEnum;
  /** The timestamp at which this operation was started */
  start_date: number;
  /** The username of the user who started this operation */
  start_user: string;
  /** The timestamp at which this operation was finished */
  end_date: string;
  /** The username of the user who finished this operation */
  end_user: string;
  /** The hash of the model this operation relates to */
  hash: number;
  /** The name of the branch this operation relates to */
  branch: string;
  /** The comment provided by the user */
  comment: string;
  /** The timestamp at which the operation was started */
  version: string;
  /** The model ID of the repository version */
  derived_from_left: string;
  /** The model ID of the uploaded version */
  derived_from_right: string;
  /** The branch name of the repository version */
  derived_from_left_branch: string;
  /** The branch name of the uploaded version */
  derived_from_right_branch: string;
  /** ?? */
  min: string;
  /** The repository operation executed */
  operation: ModelProvenanceOperationEnum;
  /** The full project name this provenance item relates to */
  project: string;
}

/**
 * All possible provenance operations
 */
export enum ModelProvenanceOperationEnum {
  CREATE_PROJECT = 'create_project',
  RETRIEVE = 'retrieve',
  COMMIT = 'commit',
  CLONE = 'clone',
  MERGE = 'merge',
  BRANCH_CLONE = 'branch_clone',
  BRANCH_MERGE = 'branch_merge',
  UPLOAD = 'upload',
}

/** Represents a summary of provenance items over a day */
export interface ModelProvenanceSummary {
  /** Number of provenance items this day */
  cnt: number;
  /** Start of the time period */
  start_date: number;
  /** List of branch names occurring in the provenance items */
  branches: string[];
}

/** The progress of a commit operation as reported by the API */
export interface ModelQuery {
  /** Textual description of the message */
  message?: string;
  /** Timestamp of creating this message */
  timestamp?: number;
  /** Timestamp of when the operation was started */
  version?: number;
  /** Current state of the operation */
  state?: ModelQueryStateEnum;
  /** Result of comparing the old and new versions of the model */
  difResult?: ModelQueryDifResult;
}

/**
 * Represents the comparison between the repository and the uploaded model as reported by the API
 */
export interface ModelQueryDifResult {
  /** The state of the comparison */
  state?: ModelQueryDifResultStateEnum;
  /** Timestamp of when the calculation started */
  timestamp?: number;
  /** The number of conflicts found */
  cnt?: number;
  /** The conflicts found */
  conflictList?: Conflict[];
}

/**
 * Represents the state of the processing after a commit as reported by the API
 */
export enum ModelQueryDifResultStateEnum {
  COMMITTED = 'COMMITTED',
  FAILURE = 'FAILURE',
  CONFLICT = 'CONFLICT',
  LOCKED = 'LOCKED',
  UNDEFINED = 'UNDEFINED',
}

/**
 * Represents the state of the operation as reported by the API
 */
export enum ModelQueryStateEnum {
  CREATED = 'created',
  WAITING = 'waiting',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILURE = 'failure',
}

/** All possible parser name values */
export enum ParserNameEnum {
  ARCHIMATE3 = 'archimate3',
}

/**
 *  Represents a single project
 */
export interface Project {
  last_updated?: number;
  id?: string;
  name?: string;
  committer?: ProjectMember;
  documentation?: string;
  subscription?: 'public' | 'private';
  start_date?: number;
  end_date?: number;
  derived_from?: string;
  project_id?: string;
  normalized_name?: string;
  last_update_message?: string;
  permissions?: { [username: string]: ProjectPermissionLevel };
  project?: string;
  owner?: string;
  end_date2?: number;
  type_?: 'project';
}

/**
 * Represents a member of a project
 */
export interface ProjectMember {
  username: string;
  email: string;
}

/** The message returned by the project update */
export interface ProjectUpdateResponse {
  comment?: string;
  taskid?: string;
}

/** Data object representing user related attributes */
export interface UserInfo {
  /** The username of the user */
  userid: string;
  /** The path in the application that the user most recently visited */
  last_visited?: string;
  /** A set of IDs for the projects that the user has marked as favorite */
  favorite_projects?: string[];
  /** A set of IDs for the projects that the user has most recently visited */
  recent_projects?: string[];
  /** Whether or not to show the getting started screen the app home page */
  skip_welcome?: boolean;
}

export interface UserRole {
  /** The username of the user */
  userid: string;
  /** The full name of the project to which the role applies */
  project: string;
  /** The email of the user */
  email: string;
  /** The name of the role */
  role_name: string;
  /** The id of the role corresponding with the permission level */
  role_id: PermissionLevel;
}

/**
 * Search result returned by the API representing a single user
 */
export class UserSearch {
  /** The first name of the user */
  firstName: string;
  /** The last name of the user */
  lastName: string;
  /** The username of the user */
  userName: string;
  /** The email address of the user */
  email: string;
}
