import { retryBackoff } from 'backoff-rxjs';
import { of, throwError } from 'rxjs';
import { concatMap, switchMap } from 'rxjs/operators';
import {
  ModelQuery,
  ModelQueryDifResultStateEnum,
  ModelQueryStateEnum,
} from '../types';
import { checkCommitStatus } from '../check-commit-status';

export interface MonitorStatusOptions {
  /** The maximum numer of times to check the status before timing out. Defaults to 30 */
  readonly retryCount?: number;
  /** The maximum time interval at which to check the status in milliseconds. Defaults to 30 seconds */
  readonly retryIntervalMax?: number;
  /** The minimum time interval at which to check the status in milliseconds. Defaults to 1 second */
  readonly retryIntervalMin?: number;
}

export const defaultMonitorStatusOptions: MonitorStatusOptions = {
  retryCount: 30,
  retryIntervalMax: 30000,
  retryIntervalMin: 1000,
};

export function monitorStatus(
  /** The full name of the project to which the task relates */
  fullProjectName: string,
  /** The ID of the task for which to check the status */
  taskId: string,
  /** Additional parameters for the monitor status operation */
  options: MonitorStatusOptions = defaultMonitorStatusOptions
) {
  const { retryCount, retryIntervalMax, retryIntervalMin } = {
    ...defaultMonitorStatusOptions,
    ...options,
  };

  return of(1).pipe(
    // Retrieve the current operation state from the API
    switchMap(() => checkCommitStatus(taskId, fullProjectName)),
    // Throws a timeout error if the state of the operation is not and end state
    switchMap((status: ModelQuery) =>
      status.state === ModelQueryStateEnum.COMPLETED ||
      status.state === ModelQueryStateEnum.FAILURE
        ? of(status)
        : throwError('The processing timed out!')
    ),
    // Retries the status check and doubles the interval every time
    // This ensures the operation does not actually time out until the max retries are reached
    retryBackoff({
      initialInterval: retryIntervalMin,
      maxInterval: retryIntervalMax,
      maxRetries: retryCount,
    }),
    // If the end state was a failure of some sorts, throw an error
    concatMap((status: ModelQuery) =>
      status.state === ModelQueryStateEnum.FAILURE ||
      status.difResult.state === ModelQueryDifResultStateEnum.FAILURE
        ? throwError('Something went wrong while processing the model!')
        : of(status)
    )
  );
}
