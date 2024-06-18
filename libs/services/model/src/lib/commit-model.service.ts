import { Injectable } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import {
  commitJsonModel,
  commitModel,
  ConflictResolutionTemplateEnum,
  forceCommitModel,
  ModelCommit,
  ModelCommitContentTypeEnum,
  ModelQuery,
  ModelQueryDifResultStateEnum,
  monitorStatus,
} from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { TaskManagerService } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Subject } from 'rxjs';
import { exhaustMap, first } from 'rxjs/operators';
import { ConflictsService } from './conflicts.service';
import { ServicesModelModule } from './services-model.module';

export interface CommitOptions {
  readonly conflictResolutionTemplate?: ConflictResolutionTemplateEnum;
  readonly keepOriginalIds?: boolean;
}

interface CommitModelContext {
  readonly branchId: string;
  readonly comment: string;
  readonly model: File | string;
  readonly options?: CommitOptions;
  readonly how?: 'file' | 'json';
}

export interface CommitModelStoreContext {
  readonly isCommittingModel?: boolean;
}

export const defaultCommitModelServiceState: CommitModelStoreContext = {
  isCommittingModel: false,
};

@Injectable({
  providedIn: ServicesModelModule,
})
export class CommitModelService extends BasicStore<CommitModelStoreContext> {
  private readonly commitModel$ = new Subject<CommitModelContext>();
  private readonly onModelCommitted$ = new Subject<void>();

  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly conflictsService: ConflictsService,
    private readonly projectService: ProjectService,
    private readonly taskManager: TaskManagerService,
    readonly storeService: StoreService
  ) {
    super({
      defaultState: defaultCommitModelServiceState,
      name: 'CommitModelService',
      storeService,
    });
    this.init();
  }

  private init() {
    // Whenever a commit is triggered, handle the commit. Only one commit can be active at a time.
    this.commitModel$
      .pipe(
        exhaustMap(({ branchId, comment, model, options, how }) =>
          this.handleCommitModel(branchId, comment, model, options, how)
        ),
        untilDestroyed(this)
      )
      .subscribe(this.onModelCommitted$);
  }

  async commitModel(
    branchId: string,
    comment: string,
    model: File,
    options: CommitOptions = {}
  ) {
    this.commitModel$.next({
      branchId,
      comment,
      model,
      options,
      how: 'file',
    });

    return this.onModelCommitted.pipe(first()).toPromise();
  }

  async commitJsonModel(
    branchId: string,
    comment: string,
    model: string,
    options: CommitOptions = {}
  ) {
    this.commitModel$.next({
      branchId,
      comment,
      model,
      options,
      how: 'json',
    });

    return this.onModelCommitted.pipe(first()).toPromise();
  }

  get onModelCommitted() {
    return this.onModelCommitted$.asObservable();
  }

  @MonitorAsync('isCommittingModel')
  private async handleCommitModel(
    branchName: string,
    comment: string,
    model: File | string,
    { conflictResolutionTemplate, keepOriginalIds = false }: CommitOptions = {},
    how: 'file' | 'json' = 'file'
  ) {
    const [project, username] = await Promise.all([
      this.projectService.getCurrentProject(),
      this.authenticationService.get(['credentials', 'username']),
    ]);

    const task = this.taskManager.createTask();

    const commitMethods = {
      file: () =>
        commitModel(project.project, branchName, model as File, username, {
          keepOriginalIds,
          comment,
        }),
      json: () =>
        commitJsonModel(
          project.project,
          branchName,
          model as string,
          username,
          {
            comment,
          }
        ),
    };

    const commitMethod = commitMethods[how],
      uploadModel = commitMethod().toPromise();

    await task.addOperation({
      description: 'Uploading the model to the repository',
      operation: uploadModel,
    });

    // Monitor the processing of the model and continue after processing is complete
    const commitStatus = uploadModel.then((commit) =>
      monitorStatus(project.project, commit.taskId).toPromise()
    );

    await task.addOperation({
      description: 'Processing the committed model',
      operation: commitStatus,
    });

    // If no conflict resolution template is given, register the conflict set with the conflicts service
    const handleConflicts = Promise.all([commitStatus, uploadModel]).then(
      ([query, commit]) => {
        if (!conflictResolutionTemplate) {
          this.conflictsService.registerConflictsForTask(
            query,
            project,
            branchName,
            branchName,
            commit.taskId,
            {
              fromModelId: commit.taskId,
              toModelId: 'TRUNK',
              parserName: 'archimate3',
              contentType: 'archimate',
              comment: commit.comment,
            }
          );
        }
        return [query, commit] as [ModelQuery, ModelCommit];
      }
    );

    await task.addOperation({
      description: 'Checking for conflicts',
      operation: handleConflicts,
    });

    // If a conflict resolution template is given, automatically resolve the conflicts
    if (conflictResolutionTemplate) {
      const resolveConflicts = handleConflicts.then(async ([query, commit]) => {
        if (query.difResult.state === ModelQueryDifResultStateEnum.CONFLICT) {
          const forceCommit = await forceCommitModel(
            'archimate3',
            project.project,
            branchName,
            '',
            commit.taskId,
            branchName,
            'TRUNK',
            username,
            commit.comment,
            ModelCommitContentTypeEnum.JSON,
            commit.taskId,
            conflictResolutionTemplate
          ).toPromise();

          return monitorStatus(project.project, forceCommit.taskId).toPromise();
        } else {
          return query;
        }
      });

      await task.addOperation({
        description: 'Resolving the conflicts',
        operation: resolveConflicts,
      });
    }

    const executable = await task.getExecutable();

    return executable.toPromise();
  }
}
