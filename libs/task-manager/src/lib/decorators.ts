import { throwError } from 'rxjs';
import { TaskManagerModule } from './task-manager.module';
import { TaskManagerService, TaskOptions } from './task-manager.service';

function createOperation(original: any, args: any, thisArg: any) {
  try {
    return original.apply(thisArg, args);
  } catch (e) {
    return throwError(e);
  }
}

function getTaskManagerService(): TaskManagerService {
  if (!TaskManagerModule.injector) {
    throw new Error(
      'Tried running a managed task while the TaskManager module was not loaded. Please make sure the Task Manager module is imported.'
    );
  }
  return TaskManagerModule.injector.get(TaskManagerService);
}

/**
 * Method decorator for functions returning an observable.
 * Registers the observable returned by the function as a managed task with the Task Manager.
 * Returns the executable of the Task instead.
 *
 * Use this decorator whenever you need to define a task with a single step.
 */
export function ManagedTask(description?: string, options?: TaskOptions) {
  return function (
    target: Object,
    key: string | symbol,
    descriptor: PropertyDescriptor
  ) {
    const original = descriptor.value;
    descriptor.value = async function (...args: any[]) {
      const taskManagerService = getTaskManagerService();

      const operation = {
        operation: createOperation(original, args, this),
        description: description,
      };

      const task = taskManagerService.createTask([operation], options);

      const executable = await task.getExecutable();

      return executable.toPromise();
    };

    return descriptor;
  };
}
