import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

/**
 * When the value emitted by the source observable is either `null`, `undefined` or `NaN`, emit the given `defaultValue` instead
 * @param defaultValue The value to emit when the source observable emits `null`, `undefined` or `NaN`
 */
export function defaultIfFalsy<T>(
  defaultValue: T
): (source: Observable<T>) => Observable<T> {
  return (source) => source.pipe(map((value) => value ?? defaultValue));
}
