import { Injectable } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { BranchSummary, mergeBranch, monitorStatus } from '@models4insight/repository';
import { ConflictsService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { TaskManagerService } from '@models4insight/task-manager';
import { from, Subject } from 'rxjs';
import { exhaustMap, finalize, map, shareReplay, switchMap, tap, withLatestFrom } from 'rxjs/operators';

export interface BranchMergeStoreContext {
  readonly branches?: BranchSummary[];
  readonly fromBranchNames?: string[];
  readonly fromBranch?: string;
  readonly isMoveBranchesFormSubmitted?: boolean;
  readonly isMovingBranches?: boolean;
  readonly isUpdatingBranches?: boolean;
  readonly toBranchNames?: string[];
  readonly toBranch?: string;
}

export const branchMergeServiceDefaultState: BranchMergeStoreContext = {
  branches: [],
  fromBranchNames: [],
  isMovingBranches: false,
  toBranchNames: []
};

@Injectable()
export class BranchMergeService extends BasicStore<BranchMergeStoreContext> {
  private readonly moveBranches$: Subject<
    [string, string, string]
  > = new Subject<[string, string, string]>();

  constructor(
    private authenticationService: AuthenticationService,
    private conflictsService: ConflictsService,
    private projectService: ProjectService,
    private taskManager: TaskManagerService,
    storeService: StoreService
  ) {
    super({
      defaultState: branchMergeServiceDefaultState,
      name: 'BranchMergeService',
      storeService
    });
    this.init();
  }

  private init() {
    // Whenever the branches update, retrieve the set of unique branch names to display in the select boxes
    this.select('branches')
      .pipe(
        map((branches: BranchSummary[]) =>
          branches.map((branch: BranchSummary) => branch._id).sort()
        )
      )
      .subscribe(branchNames =>
        this.update({
          description: 'New branch names available',
          payload: {
            fromBranchNames: branchNames,
            toBranchNames: branchNames
          }
        })
      );

    // Whenever the move branches event triggers, execute the move. Only one move can be active at once.
    this.moveBranches$
      .pipe(
        exhaustMap(([fromBranch, toBranch, comment]) =>
          from(this.handleBranchMove(fromBranch, toBranch, comment)).pipe(
            finalize(() =>
              this.update({
                description: 'Done moving branches',
                payload: {
                  isMoveBranchesFormSubmitted: false
                }
              })
            )
          )
        )
      )
      .subscribe();
  }

  moveBranches(fromBranch: string, toBranch: string, comment: string) {
    this.moveBranches$.next([fromBranch, toBranch, comment]);
  }

  @MonitorAsync('isMovingBranches')
  private async handleBranchMove(
    fromBranch: string,
    toBranch: string,
    comment: string
  ) {
    const [project, username] = await Promise.all([
      this.projectService.getCurrentProject(),
      this.authenticationService.get(['credentials', 'username'])
    ]);

    const task = this.taskManager.createTask();

    const mergeOperation = mergeBranch(
      project.project,
      fromBranch,
      toBranch,
      username,
      { comment: comment }
    ).pipe(shareReplay());

    const mergeStatus = mergeOperation.pipe(
      switchMap(commit => monitorStatus(project.project, commit.taskId)),
      shareReplay()
    );

    const checkForConflicts = mergeStatus.pipe(
      withLatestFrom(mergeOperation),
      tap(([status, commit]) =>
        this.conflictsService.registerConflictsForTask(
          status,
          project,
          fromBranch,
          toBranch,
          commit.taskId,
          {
            comment: comment
          }
        )
      ),
      shareReplay()
    );

    await task.addOperation({
      description: `Moving the ${fromBranch} branch to the ${toBranch} branch in the repository`,
      operation: mergeOperation
    });
    await task.addOperation({
      description: `Processing the move operation`,
      operation: mergeStatus
    });
    await task.addOperation({
      description: 'Checking the model for conflicts',
      operation: checkForConflicts
    });

    const executable = await task.getExecutable()

    return executable.toPromise();
  }
}
