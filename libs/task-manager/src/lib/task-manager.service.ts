import { Injectable } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Logger } from '@models4insight/logger';
import { BasicStore, StoreService } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { EMPTY, from, Observable, of, range, Subject, zip, race } from 'rxjs';
import {
  catchError,
  concatMap,
  shareReplay,
  switchMap,
  switchMapTo,
  takeLast,
  takeUntil,
  tap,
} from 'rxjs/operators';
import { v4 as uuid } from 'uuid';
import { TaskManagerModule } from './task-manager.module';

const log = new Logger('TaskManager');

export interface OperationContext {
  readonly operation: Observable<any> | Promise<any>;
  readonly description?: string;
}

export interface CurrentOperationContext {
  readonly description?: string;
  readonly index?: number;
}

export interface TaskNavigationContext {
  readonly relativeTo?: ActivatedRoute;
  readonly route: string[];
}

export interface TaskOptions {
  /**
   * Whether or not to clear the task if it completes with an error. Defaults to false.
   */
  readonly clearOnError?: boolean;
  /**
   * Whether or not to clear the task if it completes successfully. Defaults to true.
   */
  readonly clearOnSuccess?: boolean;
  /**
   * Whether or not to hide the progress bar while the task is in progress. Defaults to false.
   */
  readonly isQuiet?: boolean;
  /**
   * When set, navigate to the given route if the task completes with an error
   */
  readonly navigateOnError?: TaskNavigationContext;
  /**
   * When set, navigate to the given route if the task completes successfully
   */
  readonly navigateOnSuccess?: TaskNavigationContext;
  /**
   * Whether or not to show the original error message when an error occurs. Defaults to false.
   */
  readonly showDetailedErrorDescription?: boolean;
}

export interface TaskContext {
  readonly currentOperation?: CurrentOperationContext;
  readonly currentState?: TaskState;
  readonly currentNavigationContext?: TaskNavigationContext;
  readonly error?: Error;
  readonly id?: string;
  readonly operations?: OperationContext[];
  readonly options?: TaskOptions;
}

export interface TaskManagerStoreContext {
  readonly tasks?: Dictionary<TaskContext>;
}

export enum TaskState {
  PENDING = 'pending',
  RUNNING = 'running',
  DONE = 'done',
  ERROR = 'error',
  INTERRUPTED = 'interrupted',
}

export const defaultTaskOptions: TaskOptions = {
  clearOnError: false,
  clearOnSuccess: true,
  isQuiet: false,
  showDetailedErrorDescription: false,
};

export class Task {
  private readonly interrupt$ = new Subject<void>();

  constructor(
    public id: string,
    private managedBy: TaskManagerService,
    private router: Router
  ) {}

  async addOperation(operation: OperationContext) {
    const operations = await this.managedBy.get(
      ['tasks', this.id, 'operations'],
      { includeFalsy: true }
    );

    this.managedBy.update({
      description: `Added an operation for task ${this.id}`,
      path: ['tasks', this.id, 'operations'],
      payload: [...operations, operation],
    });
  }

  /** Interrupts the task if it is currently running */
  interrupt() {
    this.interrupt$.next();
    this.managedBy.update({
      description: `Task ${this.id} was interrupted`,
      path: ['tasks', this.id, 'currentState'],
      payload: TaskState.INTERRUPTED,
    });
  }

  /** Returns an executable of this task */
  async getExecutable() {
    const task = await this.managedBy.get(['tasks', this.id]);

    const onStart = () =>
      this.managedBy.update({
        description: `Task ${task.id} started`,
        path: ['tasks', task.id, 'currentState'],
        payload: TaskState.RUNNING,
      });

    const pipeline = zip(
      range(0, task.operations.length),
      from(task.operations)
    ).pipe(
      // Execute each operation sequentially. Ensure each task completes by only taking at most one emission from the stream
      concatMap(([index, operation]) =>
        this.handleOperation(task.id, operation, index)
      ),
      takeLast(1)
    );

    const onComplete = () => {
      this.managedBy.update({
        description: `Task ${this.id} completed`,
        path: ['tasks', this.id, 'currentState'],
        payload: TaskState.DONE,
      });
      this.finalize(task);
    };

    const onInterrupt = () => {
      this.managedBy.update({
        description: `Task ${this.id} interrupted`,
        path: ['tasks', this.id, 'currentState'],
        payload: TaskState.INTERRUPTED,
      });
    };

    const onError = (error: Error) => {
      log.error(error);
      this.managedBy.update({
        description: `Task ${task.id} encountered an error`,
        path: ['tasks', task.id, 'error'],
        payload: error,
      });
      this.managedBy.update({
        description: `Task ${task.id} completed with an error`,
        path: ['tasks', task.id, 'currentState'],
        payload: TaskState.ERROR,
      });
      return EMPTY;
    };

    const interrupt = this.interrupt$.pipe(tap(onInterrupt));

    const tasks = of(task).pipe(
      tap(onStart),
      switchMapTo(pipeline),
      tap(onComplete),
      catchError(onError)
    );

    const executable = race(tasks, interrupt);

    return executable;
  }

  /**
   * Can be used to override the description of the current operation
   */
  set currentDescription(description: string) {
    this.managedBy.update({
      description: `Task ${this.id} description updated`,
      path: ['tasks', this.id, 'currentOperation', 'description'],
      payload: description,
    });
  }

  set currentNavigationContext(context: TaskNavigationContext) {
    this.managedBy.update({
      description: `Task ${this.id} navigation context updated`,
      path: ['tasks', this.id, 'currentNavigationContext'],
      payload: context,
    });
  }

  private finalize(task: TaskContext) {
    // When the task completed successfully...
    if (task.currentState === TaskState.DONE) {
      if (task.options.navigateOnSuccess) {
        this.navigate(task.options.navigateOnSuccess);
      }
    }
    // When the task completed with an error...
    if (task.currentState === TaskState.ERROR) {
      if (task.options.navigateOnError) {
        this.navigate(task.options.navigateOnError);
      }
    }
  }

  private handleOperation(
    taskId: string,
    operation: OperationContext,
    index: number
  ) {
    this.managedBy.update({
      description: 'Start executing operation',
      path: ['tasks', taskId, 'currentOperation'],
      payload: {
        description: operation.description || `Step ${index}`,
        index: index,
      },
    });
    return of(1).pipe(
      tap(() => log.time(taskId, operation.description)),
      switchMap(() => operation.operation),
      tap(() => log.timeEnd(taskId, operation.description))
    );
  }

  private navigate(context: TaskNavigationContext) {
    this.router.navigate(context.route, { relativeTo: context.relativeTo });
  }
}

@Injectable({
  providedIn: TaskManagerModule,
})
export class TaskManagerService extends BasicStore<TaskManagerStoreContext> {
  constructor(private router: Router, storeService: StoreService) {
    super({ name: 'TaskManagerService', storeService });
    this.init();
  }

  private init() {
    // Clean up completed tasks that can be removed from the queue
    this.watch('tasks')
      .pipe(
        concatMap((tasks) => this.handleRemoveCompletedTasks(tasks)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  createTask(
    operations: OperationContext[] = [],
    options: TaskOptions = {}
  ): Task {
    const taskId = uuid();

    this.update({
      description: `Task ${taskId} created`,
      path: ['tasks', taskId],
      payload: {
        currentState: TaskState.PENDING,
        id: taskId,
        operations: operations,
        options: { ...defaultTaskOptions, ...options },
      },
    });

    return new Task(taskId, this, this.router);
  }

  clearTask(taskId: string) {
    this.delete({
      description: `Cleared task ${taskId}`,
      path: ['tasks', taskId],
    });
  }

  private async handleRemoveCompletedTasks(tasks: TaskContext[]) {
    for (const task of tasks) {
      const clearAfterError =
          task.currentState === TaskState.ERROR && task.options.clearOnError,
        clearAfterSuccess =
          task.currentState === TaskState.DONE && task.options.clearOnSuccess;

      if (clearAfterError || clearAfterSuccess) {
        this.clearTask(task.id);
      }
    }
  }
}
