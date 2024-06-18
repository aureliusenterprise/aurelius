import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';
import {
  ModelQuery,
  ModelQueryDifResultStateEnum,
  ModelQueryStateEnum,
  Project,
} from '@models4insight/repository';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { combineLatest, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ServicesModelModule } from './services-model.module';

/**
 * Represents the conflicts for a single commit or moved branch
 */
export interface ConflictSetContext {
  readonly project: Project;
  readonly parserName: string;
  readonly fromBranchName: string;
  readonly toBranchName: string;
  readonly fromModelId: string;
  readonly toModelId: string;
  readonly comment: string;
  readonly contentType: string;
  readonly taskId: string;
  readonly conflictSet: ModelQuery;
  readonly addListLeft: Set<string>;
  readonly addListRight: Set<string>;
  readonly deleteListLeft: Set<string>;
  readonly deleteListRight: Set<string>;
}

/**
 * Data object for the state of the conflicts service.
 */
export interface ConflictsStoreContext {
  /** Index of conflict sets keyed by their task ID */
  readonly conflictSetsByTaskId?: Dictionary<ConflictSetContext>;
  /** Groups conflict sets by their associated project IDs */
  readonly conflictSetsPerProject?: Dictionary<string[]>;
}

@Injectable({
  providedIn: ServicesModelModule,
})
export class ConflictsService extends BasicStore<ConflictsStoreContext> {
  constructor(storeService: StoreService) {
    super({
      name: 'ConflictsService',
      storeService,
    });
    this.init();
  }

  private init() {
    // Whenever the conflict sets update, create an index of the conflict sets per project
    this.select('conflictSetsByTaskId')
      .pipe(untilDestroyed(this))
      .subscribe((conflictSetsByTaskId) =>
        this.groupConflictSetsByProjectId(conflictSetsByTaskId)
      );
  }

  /**
   * Registers a new conflict set
   */
  addConflictSet(
    /** The parser that should be used to interpret the model */
    parserName: string,
    /** The project to which the model belongs */
    project: Project,
    /** The source branch for the commit/move */
    fromBranchName: string,
    /** The target branch for the commit/move */
    toBranchName: string,
    /** The source model ID for the commit/move */
    fromModelId: string,
    /** The target model ID for the commit/move */
    toModelId: string,
    /** The original comment provided by the user */
    comment: string,
    /** The task ID as assigned by the API */
    taskId: string,
    /** The content type in which the model was submitted */
    contentType: string,
    /** The server response indicating there was a conflict */
    conflictSet: ModelQuery
  ) {
    this.update({
      description: 'New conflict set available',
      path: ['conflictSetsByTaskId', taskId],
      payload: {
        parserName: parserName,
        project: project,
        taskId: taskId,
        fromBranchName: fromBranchName,
        toBranchName: toBranchName,
        fromModelId: fromModelId,
        toModelId: toModelId,
        conflictSet: conflictSet,
        comment: comment,
        contentType: contentType,
        addListLeft: new Set<string>(),
        addListRight: new Set<string>(),
        deleteListLeft: new Set<string>(),
        deleteListRight: new Set<string>(),
      },
    });
  }

  /**
   * Retrieves the specific conflict set identified by the given task ID as a `Promise`
   * @param taskId The identifier of the conflict set
   */
  async getConflictSet(taskId: string): Promise<ConflictSetContext> {
    return this.get(['conflictSetsByTaskId', taskId]);
  }

  /**
   * Returns the conflict sets for the project with the given `projectId` as a `Promise`
   * @param projectId The id of the project for which to retrieve the conflict sets
   */
  async getConflictSetsForProject(projectId: string) {
    const [conflictSetsByTaskId, taskIds] = await Promise.all([
      this.get('conflictSetsByTaskId'),
      this.get(['conflictSetsPerProject', projectId]),
    ]);

    return taskIds.map((taskId) => conflictSetsByTaskId[taskId]);
  }

  /**
   * Returns whether or not the given task indicates any conflicts
   * @param modelQuery The task that should be checked
   */
  hasConflicts(modelQuery: ModelQuery) {
    return (
      modelQuery?.state === ModelQueryStateEnum.COMPLETED &&
      modelQuery?.difResult?.state === ModelQueryDifResultStateEnum.CONFLICT
    );
  }

  /**
   * Checks the given server response whether it indicates any conflicts.
   * If so, registers a new conflict set.
   */
  registerConflictsForTask(
    modelQuery: ModelQuery,
    project: Project,
    fromBranchName: string,
    toBranchName: string,
    taskId: string,
    options: {
      fromModelId?: string;
      toModelId?: string;
      parserName?: 'archimate3';
      contentType?: 'archimate';
      comment?: string;
    } = {}
  ) {
    const config = {
      fromModelId: 'TRUNK',
      toModelId: 'TRUNK',
      parserName: 'archimate3',
      contentType: 'archimate',
      comment: '',
      ...options,
    };

    if (this.hasConflicts(modelQuery)) {
      this.addConflictSet(
        config.parserName,
        project,
        fromBranchName,
        toBranchName,
        config.fromModelId,
        config.toModelId,
        config.comment,
        taskId,
        config.contentType,
        modelQuery
      );
    }
  }

  /**
   * Unregisters a conflict set identified by the given `taskId`
   */
  removeConflictSet(
    /** The task ID which identifies the conflict set */
    taskId: string
  ): void {
    this.delete({
      description: 'Removed a conflict set',
      path: ['conflictSetsByTaskId', taskId],
    });
  }

  /**
   * Retrieves an `Observable` stream of the specific conflict set identified by the given `taskId`
   * @param taskId The identifier of the conflict set
   */
  selectConflictSet(taskId: string): Observable<ConflictSetContext> {
    return this.select(['conflictSetsByTaskId', taskId]);
  }

  /**
   * Returns an `Observable` stream of the conflict sets for the project with the given `projectId`
   * @param projectId The id of the project for which to retrieve the conflict sets
   */
  selectConflictSetsForProject(projectId: string) {
    return combineLatest([
      this.select('conflictSetsByTaskId'),
      this.select(['conflictSetsPerProject', projectId]),
    ]).pipe(
      map(([conflictSetsByTaskId, taskIds]) =>
        taskIds
          .map((taskId) => conflictSetsByTaskId[taskId])
          .filter((conflictSet) => !!conflictSet)
      )
    );
  }

  private groupConflictSetsByProjectId(
    conflictSetsByTaskId: Dictionary<ConflictSetContext>
  ) {
    const conflictSetsPerProject = Object.entries(conflictSetsByTaskId).reduce(
      (result, [taskId, conflictSet]) => ({
        ...result,
        [conflictSet.project.id]: [
          ...(result[conflictSet.project.id] ?? []),
          taskId,
        ],
      }),
      {} as Dictionary<string[]>
    );

    this.update({
      description: 'New conflict sets per project available',
      payload: {
        conflictSetsPerProject,
      },
    });
  }
}
