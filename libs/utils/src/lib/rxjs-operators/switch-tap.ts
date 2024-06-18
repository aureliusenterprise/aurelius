import { concat, MonoTypeOperatorFunction, Observable, of } from 'rxjs';
import { ignoreElements, switchMap } from 'rxjs/operators';

/**
 * Perform an asynchronous side effect for every emission of the source Observable, but return an observable that is identical to the source.
 */
export function switchTap<T, R>(
  next: (x: T) => Observable<R>
): MonoTypeOperatorFunction<T>;
export function switchTap<R>(
  observable: Observable<R>
): MonoTypeOperatorFunction<R>;
export function switchTap<T, R>(
  arg: Observable<T> | ((x: T) => Observable<R>)
): MonoTypeOperatorFunction<T> {
  const next: (x: any) => Observable<T | R> =
    typeof arg === 'function' ? arg : (x: any): Observable<T> => arg;
  return switchMap((value) =>
    concat(next(value).pipe(ignoreElements()), of(value))
  );
}
