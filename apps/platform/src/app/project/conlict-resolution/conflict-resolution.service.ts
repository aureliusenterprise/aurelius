import { Injectable } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { Conflict, ConflictChangeTypeEnum, ConflictResolutionTemplateEnum, ConflictSide, forceCommitModel, getModelConflict, ModelCommit, monitorStatus } from '@models4insight/repository';
import { ConflictSetContext, ConflictsService } from '@models4insight/services/model';
import { ManagedTask, TaskManagerService } from '@models4insight/task-manager';
import { combineLatest, from, of, Subject } from 'rxjs';
import { concatMap, exhaustMap, filter, first, map, scan, shareReplay, switchMap, tap, withLatestFrom } from 'rxjs/operators';

export interface SaveContext {
  conflict: Conflict;
  operation: 'add' | 'delete';
  side: ConflictSide;
}

export const ConflictResolutionTemplate = ConflictResolutionTemplateEnum;

interface ConflictMap {
  [index: number]: Conflict;
}

export interface ConflictResolutionStoreContext {
  readonly appliedTemplate?: ConflictResolutionTemplateEnum;
  readonly conflictList?: Conflict[];
  readonly conflictMap?: ConflictMap;
  readonly currentContext?: ConflictSetContext;
  readonly currentOffset?: number;
  readonly isEndReached?: boolean;
  readonly isLoadingConflicts?: boolean;
  readonly isResolvingConflicts?: boolean;
  readonly resolvedConflictsCount?: number;
  readonly selectedConflict?: Conflict;
  readonly selectedTemplate?: ConflictResolutionTemplateEnum;
}

const CONFLICT_BATCH_SIZE = 20;

@Injectable()
export class ConflictResolutionService extends BasicStore<
  ConflictResolutionStoreContext
> {
  private readonly applySelectedTemplate$: Subject<void> = new Subject<void>();
  private readonly resolveConflicts$: Subject<void> = new Subject<void>();

  constructor(
    private authenticationService: AuthenticationService,
    private conflictsService: ConflictsService,
    private taskManager: TaskManagerService,
    storeService: StoreService
  ) {
    super({ name: 'ConflictResolutionService', storeService });
    this.init();
  }

  private init() {
    // Whenever the current context changes, reset the context view state
    this.select(['currentContext', 'taskId'], { includeFalsy: true }).subscribe(
      () => {
        this.update({
          description: 'Applying context view state default values',
          payload: {
            selectedTemplate: ConflictResolutionTemplate.MANUAL,
            appliedTemplate: ConflictResolutionTemplate.MANUAL,
            resolvedConflictsCount: 0,
            isLoadingConflicts: false,
            isEndReached: false
          }
        });
      }
    );

    // Whenever the resolve conflicts event fires, resolve the given conflicts
    this.resolveConflicts$
      .pipe(
        withLatestFrom(
          this.select('currentContext', { includeFalsy: true }),
          this.select('appliedTemplate'),
          this.select('resolvedConflictsCount')
        ),
        filter(
          ([, context, template, count]) =>
            // If the current template is manual, all conflicts should be resolved
            context &&
            (template !== ConflictResolutionTemplate.MANUAL ||
              count === context.conflictSet.difResult.cnt)
        ),
        exhaustMap(([, context, template]) =>
          this.handleResolveConflicts(context, template)
        )
      )
      .subscribe();

    // Whenever the apply selected template event fires, set the applied template
    this.applySelectedTemplate$
      .pipe(withLatestFrom(this.select('selectedTemplate')))
      .subscribe(([, template]) =>
        this.update({
          description: 'Applied selected conflict resolution template',
          payload: {
            appliedTemplate: template
          }
        })
      );

    // Whenever the applied template changes, apply the new template to the current context
    this.select('appliedTemplate')
      .pipe(
        withLatestFrom(
          this.select('conflictList'),
          this.select('currentContext')
        )
      )
      .subscribe(([template, conflicts, context]) =>
        this.applyConflictResolutionTemplate(template, conflicts, context)
      );

    // Whenever a new context is selected, retrieve a new batch of conflicts
    this.select(['currentContext', 'taskId']).subscribe(() => {
      this.nextBatch(0);
    });

    // Whenever the current offset changes, retrieve a new batch of conflicts
    combineLatest([this.select('currentOffset'), this.select('currentContext')])
      .pipe(
        concatMap(([offset, context]) =>
          from(this.handleGetBatch(offset, context)).pipe(
            map(batch => [batch, offset])
          )
        ),
        scan((acc, [batch, offset]: [ConflictMap, number]) => {
          return offset > 0 ? { ...acc, ...batch } : batch;
        }, {} as ConflictMap)
      )
      .subscribe(batchMap =>
        this.update({
          description: 'New conflict map available',
          payload: {
            conflictMap: batchMap
          }
        })
      );

    // Whenever the conflict map updates, generate a new list of conflicts to show on the page
    this.select('conflictMap').subscribe(conflictMap => {
      const conflicts = Object.values(conflictMap);
      this.update({
        description: 'List of conflicts updated',
        payload: {
          conflictList: conflicts
        }
      });
    });

    // Whenever the list of conflicts updates, count how many conflicts are currently resolved
    this.select('conflictList')
      .pipe(
        map(
          conflicts =>
            conflicts.filter(conflict => !!conflict.resolution).length
        )
      )
      .subscribe(resolvedConflicts =>
        this.update({
          description: 'Count of resolved conflicts updated',
          payload: {
            resolvedConflictsCount: resolvedConflicts
          }
        })
      );

    // Whenever the list of conflicts updates, apply the selected template if it's not set to manual
    this.select('conflictList')
      .pipe(
        withLatestFrom(
          this.select('currentContext'),
          this.select('selectedTemplate')
        ),
        filter(
          ([, , template]) => template !== ConflictResolutionTemplate.MANUAL
        )
      )
      .subscribe(([conflicts, context, template]) =>
        this.applyConflictResolutionTemplate(template, conflicts, context)
      );
  }

  save(context: ConflictSetContext, saveContext: SaveContext) {
    const id = saveContext.side.id;

    if (saveContext.operation === 'add') {
      if (saveContext.side.source === 'left') {
        this.conflictsService.update({
          description: 'Conflict resolved as add left',
          path: ['conflictSetsByTaskId', context.taskId],
          payload: Object.assign(context, {
            addListLeft: new Set([...Array.from(context.addListLeft), id]),
            addListRight: new Set(
              Array.from(context.addListRight).filter(item => item !== id)
            ),
            deleteListLeft: new Set(
              Array.from(context.deleteListLeft).filter(item => item !== id)
            ),
            deleteListRight: new Set(
              Array.from(context.deleteListRight).filter(item => item !== id)
            )
          })
        });
      } else {
        this.conflictsService.update({
          description: 'Conflict resolved as add right',
          path: ['conflictSetsByTaskId', context.taskId],
          payload: Object.assign(context, {
            addListRight: new Set([...Array.from(context.addListRight), id]),
            addListLeft: new Set(
              Array.from(context.addListLeft).filter(item => item !== id)
            ),
            deleteListLeft: new Set(
              Array.from(context.deleteListLeft).filter(item => item !== id)
            ),
            deleteListRight: new Set(
              Array.from(context.deleteListRight).filter(item => item !== id)
            )
          })
        });
      }
    } else {
      if (saveContext.side.source === 'left') {
        this.conflictsService.update({
          description: 'Conflict resolved as delete left',
          path: ['conflictSetsByTaskId', context.taskId],
          payload: Object.assign(context, {
            deleteListLeft: new Set([
              ...Array.from(context.deleteListLeft),
              id
            ]),
            addListRight: new Set(
              Array.from(context.addListRight).filter(item => item !== id)
            ),
            addListLeft: new Set(
              Array.from(context.addListLeft).filter(item => item !== id)
            ),
            deleteListRight: new Set(
              Array.from(context.deleteListRight).filter(item => item !== id)
            )
          })
        });
      } else {
        this.conflictsService.update({
          description: 'Conflict resolved as delete right',
          path: ['conflictSetsByTaskId', context.taskId],
          payload: Object.assign(context, {
            deleteListRight: new Set([
              ...Array.from(context.deleteListRight),
              id
            ]),
            addListRight: new Set(
              Array.from(context.addListRight).filter(item => item !== id)
            ),
            addListLeft: new Set(
              Array.from(context.addListLeft).filter(item => item !== id)
            ),
            deleteListLeft: new Set(
              Array.from(context.deleteListLeft).filter(item => item !== id)
            )
          })
        });
      }
    }

    this.update({
      description: 'Set applied template to manual',
      payload: {
        selectedTemplate: ConflictResolutionTemplate.MANUAL,
        appliedTemplate: ConflictResolutionTemplate.MANUAL
      }
    });

    this.select('conflictList')
      .pipe(first())
      .subscribe(conflicts =>
        this.update({
          description: 'Conflict resolution updated',
          payload: {
            conflictList: [
              ...conflicts.filter(
                conflict => conflict !== saveContext.conflict
              ),
              Object.assign(saveContext.conflict, { resolution: 'manual' })
            ]
          }
        })
      );
  }

  resolveConflicts() {
    this.resolveConflicts$.next();
  }

  nextBatch(offset: number) {
    this.update({
      description: 'Conflict list offset updated',
      payload: { currentOffset: offset }
    });
  }

  applySelectedTemplate() {
    this.applySelectedTemplate$.next();
  }

  private applyConflictResolutionTemplate(
    template: ConflictResolutionTemplateEnum,
    conflicts: Conflict[],
    context: ConflictSetContext
  ) {
    switch (template) {
      case ConflictResolutionTemplate.REPOSITORY_ONLY: {
        this.applyRepositoryOnlyTemplate(conflicts, context);
        break;
      }
      case ConflictResolutionTemplate.UPLOAD_ONLY: {
        this.applyUploadOnlyTemplate(conflicts, context);
        break;
      }
      case ConflictResolutionTemplate.UNION_REPOSITORY: {
        this.applyUnionRepositoryTemplate(conflicts, context);
        break;
      }
      case ConflictResolutionTemplate.UNION_UPLOAD: {
        this.applyUnionUploadTemplate(conflicts, context);
        break;
      }
    }
  }

  classifyConflict(conflict: Conflict): string {
    // Removes the trailing 's' from the type name to make it singular rather than plural
    const type = conflict.type.substring(0, conflict.type.length - 1);

    if (
      conflict.leftChange === ConflictChangeTypeEnum.UNCHANGED &&
      conflict.rightChange === ConflictChangeTypeEnum.ADDED
    ) {
      return `Added a new ${type}`;
    } else if (
      conflict.leftChange === ConflictChangeTypeEnum.UNCHANGED &&
      conflict.rightChange === ConflictChangeTypeEnum.DELETED
    ) {
      return `Removed an existing ${type}`;
    } else if (
      conflict.leftChange === ConflictChangeTypeEnum.UNCHANGED &&
      conflict.rightChange === ConflictChangeTypeEnum.MODIFIED
    ) {
      return `Modified an existing ${type}`;
    } else if (
      conflict.leftChange === ConflictChangeTypeEnum.ADDED &&
      conflict.rightChange === ConflictChangeTypeEnum.UNCHANGED
    ) {
      return `A ${type} is in the repository but not in the committed model`;
    } else if (
      conflict.leftChange === ConflictChangeTypeEnum.ADDED &&
      conflict.rightChange === ConflictChangeTypeEnum.ADDED
    ) {
      return `Added a ${type} that was previously added`;
    } else if (
      conflict.leftChange === ConflictChangeTypeEnum.DELETED &&
      conflict.rightChange === ConflictChangeTypeEnum.UNCHANGED
    ) {
      return `A ${type} was previously deleted`;
    } else if (
      conflict.leftChange === ConflictChangeTypeEnum.DELETED &&
      conflict.rightChange === ConflictChangeTypeEnum.ADDED
    ) {
      return `Added a ${type} that was previously deleted`;
    } else if (
      conflict.leftChange === ConflictChangeTypeEnum.DELETED &&
      conflict.rightChange === ConflictChangeTypeEnum.MODIFIED
    ) {
      return `Modified a ${type} that was previously deleted`;
    } else if (
      conflict.leftChange === ConflictChangeTypeEnum.MODIFIED &&
      conflict.rightChange === ConflictChangeTypeEnum.UNCHANGED
    ) {
      return `A ${type} was previously deleted`;
    } else if (
      conflict.leftChange === ConflictChangeTypeEnum.MODIFIED &&
      conflict.rightChange === ConflictChangeTypeEnum.DELETED
    ) {
      return `Deleted a ${type} that was previously modified`;
    } else if (
      conflict.leftChange === ConflictChangeTypeEnum.MODIFIED &&
      conflict.rightChange === ConflictChangeTypeEnum.MODIFIED
    ) {
      return `Modified a ${type} that was previously modified`;
    } else {
      return `Unclassified`;
    }
  }

  @ManagedTask('Retrieving a new batch of conflicts')
  @MonitorAsync('isLoadingConflicts')
  private async handleGetBatch(
    offset: number,
    context: ConflictSetContext
  ): Promise<ConflictMap> {
    const conflicts = await getModelConflict(
      context.taskId,
      context.project.project,
      offset,
      CONFLICT_BATCH_SIZE
    ).toPromise();

    if (
      conflicts.difResult &&
      conflicts.difResult.conflictList &&
      conflicts.difResult.conflictList.length === 0
    ) {
      this.update({
        description: 'End of conflict list reached',
        payload: {
          isEndReached: true
        }
      });
    }

    return conflicts.difResult.conflictList.reduce(
      (acc, conflict, index) => ({ ...acc, [offset + index]: conflict }),
      {} as ConflictMap
    );
  }

  private applyRepositoryOnlyTemplate(
    conflicts: Conflict[],
    context: ConflictSetContext
  ) {
    const addListLeft = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.left &&
            (conflict.leftChange === ConflictChangeTypeEnum.ADDED ||
              conflict.leftChange === ConflictChangeTypeEnum.MODIFIED)
        )
        .map((conflict: Conflict) => conflict.left.id)
    );

    const deleteListLeft = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.left &&
            conflict.leftChange === ConflictChangeTypeEnum.DELETED
        )
        .map((conflict: Conflict) => conflict.left.id)
    );

    const addListRight = new Set<string>();

    const deleteListRight = new Set<string>();

    this.update({
      description: 'Applied repository only template',
      payload: {
        conflictList: conflicts.map(conflict =>
          Object.assign(conflict, {
            resolution: ConflictResolutionTemplate.REPOSITORY_ONLY
          })
        )
      }
    });

    this.conflictsService.update({
      description: 'Updated add and delete lists',
      path: ['conflictSetsByTaskId', context.taskId],
      payload: Object.assign(context, {
        addListLeft: addListLeft,
        deleteListLeft: deleteListLeft,
        addListRight: addListRight,
        deleteListRight: deleteListRight
      })
    });
  }

  private applyUploadOnlyTemplate(
    conflicts: Conflict[],
    context: ConflictSetContext
  ) {
    const addListLeft = new Set<string>();

    const deleteListLeft = new Set<string>();

    const addListRight = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.right &&
            (conflict.rightChange === ConflictChangeTypeEnum.ADDED ||
              conflict.rightChange === ConflictChangeTypeEnum.MODIFIED)
        )
        .map((conflict: Conflict) => conflict.right.id)
    );

    const deleteListRight = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.right &&
            conflict.rightChange === ConflictChangeTypeEnum.DELETED
        )
        .map((conflict: Conflict) => conflict.right.id)
    );

    this.update({
      description: 'Applied upload only template',
      payload: {
        conflictList: conflicts.map(conflict =>
          Object.assign(conflict, {
            resolution: ConflictResolutionTemplate.UPLOAD_ONLY
          })
        )
      }
    });

    this.conflictsService.update({
      description: 'Updated add and delete lists',
      path: ['conflictSetsByTaskId', context.taskId],
      payload: Object.assign(context, {
        addListLeft: addListLeft,
        deleteListLeft: deleteListLeft,
        addListRight: addListRight,
        deleteListRight: deleteListRight
      })
    });
  }

  private applyUnionRepositoryTemplate(
    conflicts: Conflict[],
    context: ConflictSetContext
  ) {
    const addListLeft = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.left &&
            (conflict.leftChange === ConflictChangeTypeEnum.ADDED ||
              conflict.leftChange === ConflictChangeTypeEnum.MODIFIED)
        )
        .map((conflict: Conflict) => conflict.left.id)
    );

    const deleteListLeft = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.left &&
            conflict.leftChange === ConflictChangeTypeEnum.DELETED
        )
        .map((conflict: Conflict) => conflict.left.id)
    );

    const addListRight = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.right &&
            conflict.leftChange === ConflictChangeTypeEnum.UNCHANGED &&
            (conflict.rightChange === ConflictChangeTypeEnum.ADDED ||
              conflict.rightChange === ConflictChangeTypeEnum.MODIFIED)
        )
        .map((conflict: Conflict) => conflict.right.id)
    );

    const deleteListRight = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.right &&
            conflict.leftChange === ConflictChangeTypeEnum.UNCHANGED &&
            conflict.rightChange === ConflictChangeTypeEnum.DELETED
        )
        .map((conflict: Conflict) => conflict.right.id)
    );

    this.update({
      description: 'Applied union repository template',
      payload: {
        conflictList: conflicts.map(conflict =>
          Object.assign(conflict, {
            resolution: ConflictResolutionTemplate.UNION_REPOSITORY
          })
        )
      }
    });

    this.conflictsService.update({
      description: 'Updated add and delete lists',
      path: ['conflictSetsByTaskId', context.taskId],
      payload: Object.assign(context, {
        addListLeft: addListLeft,
        deleteListLeft: deleteListLeft,
        addListRight: addListRight,
        deleteListRight: deleteListRight
      })
    });
  }

  private applyUnionUploadTemplate(
    conflicts: Conflict[],
    context: ConflictSetContext
  ) {
    const addListLeft = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.left &&
            conflict.rightChange === ConflictChangeTypeEnum.UNCHANGED &&
            (conflict.leftChange === ConflictChangeTypeEnum.ADDED ||
              conflict.leftChange === ConflictChangeTypeEnum.MODIFIED)
        )
        .map((conflict: Conflict) => conflict.left.id)
    );

    const deleteListLeft = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.left &&
            conflict.rightChange === ConflictChangeTypeEnum.UNCHANGED &&
            conflict.leftChange === ConflictChangeTypeEnum.DELETED
        )
        .map((conflict: Conflict) => conflict.left.id)
    );

    const addListRight = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.right &&
            (conflict.rightChange === ConflictChangeTypeEnum.ADDED ||
              conflict.rightChange === ConflictChangeTypeEnum.MODIFIED)
        )
        .map((conflict: Conflict) => conflict.right.id)
    );

    const deleteListRight = new Set<string>(
      conflicts
        .filter(
          (conflict: Conflict) =>
            conflict.right &&
            conflict.rightChange === ConflictChangeTypeEnum.DELETED
        )
        .map((conflict: Conflict) => conflict.right.id)
    );

    this.update({
      description: 'Applied union upload template',
      payload: {
        conflictList: conflicts.map(conflict =>
          Object.assign(conflict, {
            resolution: ConflictResolutionTemplate.UNION_UPLOAD
          })
        )
      }
    });

    this.conflictsService.update({
      description: 'Updated add and delete lists',
      path: ['conflictSetsByTaskId', context.taskId],
      payload: Object.assign(context, {
        addListLeft: addListLeft,
        deleteListLeft: deleteListLeft,
        addListRight: addListRight,
        deleteListRight: deleteListRight
      })
    });
  }

  @MonitorAsync('isResolvingConflicts')
  private async handleResolveConflicts(
    context: ConflictSetContext,
    appliedTemplate: ConflictResolutionTemplateEnum = ConflictResolutionTemplate.MANUAL
  ) {
    const conflictResolution = of([context, appliedTemplate] as [
      ConflictSetContext,
      ConflictResolutionTemplateEnum
    ])
      .pipe(
        withLatestFrom(this.authenticationService.credentials()),
        switchMap(([[context, appliedTemplate], credentials]) =>
          forceCommitModel(
            context.parserName,
            context.project.project,
            context.fromBranchName,
            '',
            context.fromModelId,
            context.toBranchName,
            context.toModelId,
            credentials.username,
            context.comment,
            context.contentType,
            context.taskId,
            appliedTemplate,
            Array.from(context.addListLeft),
            Array.from(context.addListRight),
            Array.from(context.deleteListLeft),
            Array.from(context.deleteListRight)
          )
        )
      )
      .pipe(shareReplay());

    const resolutionStatus = conflictResolution.pipe(
      switchMap((status: ModelCommit) =>
        monitorStatus(context.project.project, status.taskId)
      ),
      tap(status => {
        this.conflictsService.removeConflictSet(context.taskId);
        this.delete({
          description: 'Conflict list reset',
          path: ['conflictList']
        });
        this.delete({
          description: 'Conflict map reset',
          path: ['conflictMap']
        });
        this.delete({
          description: 'Current conflicts reset',
          path: ['currentContext']
        });
        this.delete({
          description: 'Applied tempalte reset',
          path: ['appliedTemplate']
        });
        this.delete({
          description: 'Selected conflict reset',
          path: ['selectedConflict']
        });
        this.delete({
          description: 'Resolved conflicts count reset',
          path: ['resolvedConflictsCount']
        });
      })
    );

    const task = this.taskManager.createTask([
      {
        description:
          'Resolving conflicts with the previous version of the model',
        operation: conflictResolution
      },
      {
        description: 'Processing the conflict resolution',
        operation: resolutionStatus
      }
    ]);

    const executable = await task.getExecutable();

    return executable.toPromise();
  }
}
