import { Observable, Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { OnDestroy } from '@angular/core';

const untilDestroyedSymbol = Symbol('untilDestroyed');

/**
 * RxJS operator that stops emissions from the source `Observable` when the specified method is called on the given object.
 * This operator provides a convenient overload which hooks into the `OnDestroy` Angular lifecycle event on an Angular Component, Directive or Service.
 * By default, references the `ngOnDestroy` lifecycle hook.
 *
 * When using the default, `ngOnDestroy` must be present on the referenced component or service, even if the implementation of the given method is empty.
 *
 * **IMPORTANT**: Add the `untilDestroyed` operator as the last one to prevent leaks with intermediate observables in the
 * operator chain.
 *
 * @example
 * export class ExampleComponent implements OnInit, OnDestroy {
 *                ngOnInit() {
 *                  // This stream prints a message to the console every second until this component is destroyed
 *                  interval(1000)
 *                    .pipe(untilDestroyed(this))
 *                    .subscribe(console.log);
 *                 }
 *
 *                // This method must be present, even if empty.
 *                ngOnDestroy() {
 *                  // To protect you, an error will be thrown if it doesn't exist.
 *                }
 * }
 */
export function untilDestroyed<T>(
  /** The parent Angular component or object instance. */
  instance: OnDestroy
): (source: Observable<T>) => Observable<T>;
export function untilDestroyed<T>(
  /** The parent Angular component or object instance. */
  instance: object,
  /** The method to hook on. Defaults to `ngOnDestroy`. */
  destroyMethodName: string = 'ngOnDestroy'
): (source: Observable<T>) => Observable<T> {
  return (source: Observable<T>) => {
    const originalDestroy = instance[destroyMethodName];
    const hasDestroyFunction = typeof originalDestroy === 'function';

    if (!hasDestroyFunction) {
      throw new Error(
        `${instance.constructor.name} is using untilDestroyed but doesn't implement ${destroyMethodName}`
      );
    }

    if (!instance[untilDestroyedSymbol]) {
      instance[untilDestroyedSymbol] = new Subject();

      instance[destroyMethodName] = function () {
        if (hasDestroyFunction) {
          originalDestroy.apply(this, arguments);
        }
        instance[untilDestroyedSymbol].next();
        instance[untilDestroyedSymbol].complete();
      };
    }

    return source.pipe(takeUntil<T>(instance[untilDestroyedSymbol]));
  };
}
