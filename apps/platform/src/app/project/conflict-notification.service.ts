import { Injectable, OnDestroy } from '@angular/core';
import { ConflictsService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { TaskManagerService } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { from } from 'rxjs';
import { concatMap, switchMap, tap } from 'rxjs/operators';

// TODO: Add Angular decorator.
@Injectable()
export class ConflictNotificationService implements OnDestroy {
  constructor(
    private readonly conflictsService: ConflictsService,
    private readonly projectService: ProjectService,
    private readonly taskManager: TaskManagerService
  ) {}

  ngOnDestroy() {}

  init() {
    // Notifies the user whenever new conflict sets are added
    this.projectService
      .select('projectId')
      .pipe(
        switchMap(projectId =>
          this.conflictsService.watch(['conflictSetsPerProject', projectId], {
            includeFalsy: true
          })
        ),
        concatMap(taskIds => this.handleCreateConflictNotification(taskIds)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  private async handleCreateConflictNotification(taskIds: string[]) {
    if (taskIds?.length > 0) {
      const task = this.taskManager.createTask();

      // For navigation, assume all given conflict sets belong to the same project
      const operation = from(
        this.conflictsService.getConflictSet(taskIds[0])
      ).pipe(
        tap(conflictSet => {
          task.currentNavigationContext = {
            route: ['project', conflictSet.project.id, 'conflicts']
          };
          task.interrupt();
        })
      );

      await task.addOperation({
        description:
          'The committed model has conflicts with the previous version',
        operation
      });

      const executable = await task.getExecutable();

      return executable.toPromise();
    }
  }
}
