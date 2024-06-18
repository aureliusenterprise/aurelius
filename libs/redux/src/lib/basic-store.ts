import { SubType } from '@models4insight/utils';
import { clone, get, omit, setWith } from 'lodash';
import { Observable, of, Subject } from 'rxjs';
import { finalize, switchMapTo, tap } from 'rxjs/operators';
import {
  AbstractStore,
  AbstractStoreOptions,
  RootReducer,
} from './abstract-store';
import {
  Action,
  ActionType,
  DeleteAction,
  SetAction,
  UpdateAction,
} from './action';
import { StoreContext } from './store';

/**
 * Returns a new instance of the given `state` which omits the entry at the given `path`.
 * If no `path` is given, or if the given `path` is empty, returns an empty `state`.
 */
export function reduceDelete<CONTEXT extends StoreContext = StoreContext>(
  state: CONTEXT,
  { path }: DeleteAction
): CONTEXT {
  return !path || path.length === 0
    ? ({} as CONTEXT)
    : path.length === 1
    ? (omit(state, path) as CONTEXT)
    : setWith(
        clone(state),
        path.slice(0, path.length - 1),
        omit(get(state, path.slice(0, path.length - 1)), path[path.length - 1]),
        clone
      );
}

/**
 * Returns a new instance of the given `payload`, replacing the given `state`.
 */
export function reduceSet<CONTEXT extends StoreContext = StoreContext>(
  state: CONTEXT,
  { payload }: SetAction<CONTEXT>
): CONTEXT {
  return clone(payload);
}

/**
 * Returns a new instance of the given `state` where any entry at the given `path` has been replaced with the given `payload`.
 * If no `path` is given, or if the given `path` is empty, the given `payload` is assigned to the given `state`.
 */
export function reduceUpdate<CONTEXT extends StoreContext = StoreContext>(
  state: CONTEXT,
  { path, payload }: UpdateAction<CONTEXT>
): CONTEXT {
  return !path || path.length === 0
    ? Object.assign(state, clone(payload))
    : // Make a clone of the current state and the payload to ensure the state is never modified in place
      setWith(clone(state), path, payload, clone);
}

const rootReducers: { [type in ActionType]?: RootReducer } = {
  [ActionType.SET]: reduceSet,
  [ActionType.UPDATE]: reduceUpdate,
  [ActionType.DELETE]: reduceDelete,
};

export interface MonitorAsyncOptions {
  /** Subject to push an event to when the operation finishes */
  onComplete?: Subject<void>;
  /**Reference to the store which defines the given indicator property */
  store?: BasicStore<any>;
}

/**
 * Decorator function which wraps a reducer to switch the given property of a `BasicStore` to `true` when the reducer starts, and `false` after it has completed.
 *
 * You can use this decorator inside of a `BasicStore` without providing the `store` parameter.
 * When using this decorator outside of a `BasicStore`, please provide a reference to the `BasicStore` which defines the given indicator property.
 */
export function MonitorAsync<T extends (...args: any[]) => Promise<any>>(
  /* Key or path to the property of the `BasicStore` which indicates the state of the operation */
  indicatorProperty: string | string[],
  /* Reference to the store which defines the given indicator property */
  options?: MonitorAsyncOptions
);
export function MonitorAsync<T extends (...args: any[]) => Observable<any>>(
  /* Key or path to the property of the BasicStore which indicates the state of the operation */
  indicatorProperty: string | string[],
  options?: MonitorAsyncOptions
);
export function MonitorAsync<
  T extends (...args: any[]) => Promise<any> | Observable<any>
>(
  indicatorProperty: string | string[],
  { onComplete, store }: MonitorAsyncOptions = {}
) {
  return function (
    target: BasicStore<any>,
    key: string | symbol,
    descriptor: TypedPropertyDescriptor<T>
  ) {
    const original = descriptor.value;
    descriptor.value = function (this: Function, ...args: any[]) {
      const originalResult = original.apply(this, args);
      return (store ?? target).monitorAsync.apply(this, [
        originalResult,
        indicatorProperty,
        onComplete,
      ]);
    } as any;
    return descriptor;
  };
}

/**
 * This is an implementation of a store supporting basic CRUD operations.
 */
export abstract class BasicStore<
  CONTEXT extends StoreContext = {}
> extends AbstractStore<CONTEXT, Action<CONTEXT>> {
  constructor(options: AbstractStoreOptions<CONTEXT> = {}) {
    super({
      ...options,
      rootReducers: { ...options.rootReducers, ...rootReducers },
    });
  }
  /**
   * Dispatch a delete operation, removing an entry in the current state
   * @param {Object} options
   * @param {String} options.description    A short explanation of the update
   * @param {String} options.path           The path of the entry to update
   */
  delete(options?: { description?: string; path?: [] }): void;
  delete<P extends keyof CONTEXT>(options?: {
    description?: string;
    path?: [P];
  }): void;
  delete<P extends keyof CONTEXT, Q extends keyof CONTEXT[P]>(options?: {
    description?: string;
    path?: [P, Q];
  }): void;
  delete<
    P extends keyof CONTEXT,
    Q extends keyof CONTEXT[P],
    R extends keyof CONTEXT[P][Q]
  >(options?: { description?: string; path?: [P, Q, R] }): void;
  delete<
    P extends keyof CONTEXT,
    Q extends keyof CONTEXT[P],
    R extends keyof CONTEXT[P][Q],
    S extends keyof CONTEXT[P][Q][R]
  >(options?: { description?: string; path?: [P, Q, R, S] }): void;
  delete(
    options: { description?: string; path?: (string | number)[] } = {}
  ): void {
    this.dispatch({
      type: ActionType.DELETE,
      description: options.description,
      path: options.path,
    });
  }

  /**
   * Wraps a reducer in an asynchronous operation to switch the given indicator property to true when it starts running, and false after it has completed..
   * @param {Observable<T>} operation         The operation to be run
   * @param {keyof CONTEXT} indicatorProperty The key or path of the property with which to indicate the process of the operation. The given key should map to a boolean type.
   */
  monitorAsync<K extends keyof SubType<CONTEXT, boolean>, P, R>(
    operation: Observable<R>,
    indicatorProperty: K,
    onComplete?: Subject<void>
  ): Observable<R>;
  monitorAsync<
    L extends keyof CONTEXT,
    K extends keyof SubType<CONTEXT[L], boolean>,
    R
  >(
    operation: Observable<R>,
    indicatorProperty: [L, K],
    onComplete?: Subject<void>
  ): Observable<R>;
  monitorAsync<
    L extends keyof CONTEXT,
    M extends keyof CONTEXT[L],
    K extends keyof SubType<CONTEXT[L][M], boolean>,
    R
  >(
    operation: Observable<R>,
    indicatorProperty: [L, M, K],
    onComplete?: Subject<void>
  ): Observable<R>;
  monitorAsync<
    L extends keyof CONTEXT,
    M extends keyof CONTEXT[L],
    N extends keyof CONTEXT[L][M],
    K extends keyof SubType<CONTEXT[L][M][N], boolean>,
    R
  >(
    operation: Observable<R>,
    indicatorProperty: [L, M, N, K],
    onComplete?: Subject<void>
  ): Observable<R>;
  monitorAsync<
    L extends keyof CONTEXT,
    M extends keyof CONTEXT[L],
    N extends keyof CONTEXT[L][M],
    O extends keyof CONTEXT[L][M][N],
    K extends keyof SubType<CONTEXT[L][M][N][O], boolean>,
    R
  >(
    operation: Observable<R>,
    indicatorProperty: [L, M, N, O, K],
    onComplete?: Subject<void>
  ): Observable<R>;
  monitorAsync<R>(
    operation: Observable<R>,
    indicatorProperty: any,
    onComplete?: Subject<void>
  ): Observable<R> {
    if (!Array.isArray(indicatorProperty)) {
      indicatorProperty = [indicatorProperty];
    }
    const setIndicatorState = (state: boolean) =>
      this.update({
        description: `Set ${indicatorProperty} to ${Boolean(state)
          .toString()
          .toUpperCase()}`,
        path: indicatorProperty,
        payload: state,
      } as any);

    return of(1).pipe(
      tap(() => setIndicatorState(true)),
      switchMapTo(operation),
      finalize(() => {
        setIndicatorState(false);
        onComplete?.next();
      })
    );
  }

  /**
   * Dispatch a set operation, replacing the current state
   * @param {Object} options
   * @param {String} options.description    A short explanation of the update
   * @param {any} options.payload           The new state
   */
  set(options: { description?: string; payload?: CONTEXT } = {}): void {
    this.dispatch({
      type: ActionType.SET,
      description: options.description,
      payload: options.payload,
    });
  }

  /**
   * Dispatch an update operation, modifying the current state
   * @param {Object} options
   * @param {String} options.description    A short explanation of the update
   * @param {String} options.path           The path of the entry to update
   * @param {any} options.payload           The new state
   */
  update(options?: {
    description?: string;
    path?: [];
    payload?: Partial<CONTEXT>;
  }): void;
  update<P extends keyof CONTEXT>(options?: {
    description?: string;
    path?: [P];
    payload?: Partial<CONTEXT[P]>;
  }): void;
  update<P extends keyof CONTEXT, Q extends keyof CONTEXT[P]>(options?: {
    description?: string;
    path?: [P, Q];
    payload?: Partial<CONTEXT[P][Q]>;
  }): void;
  update<
    P extends keyof CONTEXT,
    Q extends keyof CONTEXT[P],
    R extends keyof CONTEXT[P][Q]
  >(options?: {
    description?: string;
    path?: [P, Q, R];
    payload?: Partial<CONTEXT[P][Q][R]>;
  }): void;
  update<
    P extends keyof CONTEXT,
    Q extends keyof CONTEXT[P],
    R extends keyof CONTEXT[P][Q],
    S extends keyof CONTEXT[P][Q][R]
  >(options?: {
    description?: string;
    path?: [P, Q, R, S];
    payload?: Partial<CONTEXT[P][Q][R][S]>;
  }): void;
  update(
    options: {
      description?: string;
      path?: (string | number)[];
      payload?: any;
    } = {}
  ): void {
    this.dispatch({
      type: ActionType.UPDATE,
      description: options.description,
      path: options.path,
      payload: options.payload,
    });
  }
}
