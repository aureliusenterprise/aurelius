import { Injectable, OnDestroy } from '@angular/core';
import { Logger } from '@models4insight/logger';
import { SubType, untilDestroyed } from '@models4insight/utils';
import { cloneDeep, Dictionary, differenceWith, isEqual } from 'lodash';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import {
  distinctUntilChanged,
  filter,
  first,
  map,
  pairwise,
  pluck,
  scan,
  shareReplay,
} from 'rxjs/operators';
import { v4 as uuid } from 'uuid';
import { Action, ActionType, ResetAction } from './action';
import { Store, StoreContext } from './store';
import { StoreService } from './store.service';

const win = window as any;

export interface AbstractStoreOptions<CONTEXT> {
  /**
   * The initial state of this store. Can be restored by calling `reset()`.
   */
  defaultState?: CONTEXT;
  /**
   * The name of this store. Used to tag debug output and as a key in the `StoreService` snapshot. The store name should be unique across all stores.
   * It is recommended to choose a recognizable, human readable name for a store.
   * If no name is given, a UUID is assigned instead.
   */
  name?: string;
  /**
   * Reducers for this store keyed by action type
   */
  rootReducers?: Dictionary<RootReducer>;
  /**
   * Pass a reference to the `StoreService` if you want this store to be registered for snapshotting
   */
  storeService?: StoreService;
}

export type RootReducer<CONTEXT extends StoreContext = StoreContext> = (
  state: CONTEXT,
  action: Action<CONTEXT>
) => CONTEXT;

export const abstractStoreDefaultState: StoreContext = {};

/**
 * An abstract base store which provides some shared functionality
 */
@Injectable()
export abstract class AbstractStore<
  CONTEXT extends StoreContext,
  ACTION extends Action<CONTEXT> = Action<CONTEXT>
> implements OnDestroy, Store<CONTEXT>
{
  /**
   * Whether or not the Store is running in production mode
   */
  public static production = false;

  /**
   * The current session ID shared across all stores for debugging and telemetry
   */
  private static readonly sessionId = uuid();

  /**
   * The display name of the store
   */
  public readonly name: string;

  /**
   * The initial state of the store
   */
  protected readonly defaultState: CONTEXT;

  /**
   * Instance of the logger for this store
   */
  protected readonly logger: Logger;

  private readonly actions$ = new Subject<ACTION | ResetAction>();
  private readonly state$: BehaviorSubject<CONTEXT>;

  private readonly rootReducers: Dictionary<RootReducer> = {};

  constructor({
    storeService,
    name = uuid(),
    rootReducers = {},
    defaultState = abstractStoreDefaultState as CONTEXT,
  }: AbstractStoreOptions<CONTEXT> = {}) {
    // Set the default state of the store as a clone of the given default state in case the default state is shared between several stores
    this.defaultState = cloneDeep(defaultState);

    // Initialize the state with the given default state
    this.state$ = new BehaviorSubject<CONTEXT>(this.defaultState);

    // Add the reset operation to the given set of reducers
    this.rootReducers = {
      ...rootReducers,
      [ActionType.RESET]: () => this.reduceReset(),
    };

    // If no store name is given, a UUID is used instead
    this.name = name;

    // Initialize the logger with either the store name or the UUID.
    this.logger = new Logger(this.name);

    // Register this store with the parent service if a reference is given. This is used for error reporting.
    if (storeService) {
      storeService.register(this);
    }

    // Start up the reducer that maintains the state
    this.actions$
      .pipe(this.reducer(), untilDestroyed(this))
      .subscribe(this.state$);
  }

  /**
   * Enables production mode.
   * Disables emissions to Redux DevTools
   */
  static enableProductionMode() {
    AbstractStore.production = true;
  }

  ngOnDestroy() {
    this.actions$.complete();
    this.state$.complete();
  }

  /**
   * Returns a snapshot of the current state at the given path
   * @param path the path of the state to return
   */
  get<P extends keyof CONTEXT>(
    path: P | [P],
    options?: { includeFalsy?: boolean }
  ): Promise<CONTEXT[P]>;
  get<P extends keyof CONTEXT, Q extends keyof CONTEXT[P]>(
    path: [P, Q],
    options?: { includeFalsy?: boolean }
  ): Promise<CONTEXT[P][Q]>;
  get<
    P extends keyof CONTEXT,
    Q extends keyof CONTEXT[P],
    R extends keyof CONTEXT[P][Q]
  >(
    path: [P, Q, R],
    options?: { includeFalsy?: boolean }
  ): Promise<CONTEXT[P][Q][R]>;
  get<
    P extends keyof CONTEXT,
    Q extends keyof CONTEXT[P],
    R extends keyof CONTEXT[P][Q],
    S extends keyof CONTEXT[P][Q][R]
  >(
    path: [P, Q, R, S],
    options?: { includeFalsy?: boolean }
  ): Promise<CONTEXT[P][Q][R][S]>;
  get<
    P extends keyof CONTEXT,
    Q extends keyof CONTEXT[P],
    R extends keyof CONTEXT[P][Q],
    S extends keyof CONTEXT[P][Q][R],
    T extends keyof CONTEXT[P][Q][R][S]
  >(
    path: [P, Q, R, S, T],
    options?: { includeFalsy?: boolean }
  ): Promise<CONTEXT[P][Q][R][S][T]>;
  get(path: any, options: { includeFalsy?: boolean } = {}): Promise<any> {
    return this.select(path, options).pipe(first()).toPromise();
  }

  /**
   * Returns the store to its default state
   */
  reset() {
    this.dispatch({
      type: ActionType.RESET,
      description: 'Return to default state',
    });
  }

  /**
   * Returns an observable of the state at the given path
   * @param path the path of the state to observe
   * @param options includeFalsy - whether to include values that are falsy (e.g. undefined, null, NaN)
   */
  select<P extends keyof CONTEXT>(
    path: P | [P],
    options?: {
      /** Whether or not to include values that are falsy (e.g. undefined, null, NaN) */
      includeFalsy?: boolean;
    }
  ): Observable<CONTEXT[P]>;
  select<P extends keyof CONTEXT, Q extends keyof CONTEXT[P]>(
    path: [P, Q],
    options?: { includeFalsy?: boolean }
  ): Observable<CONTEXT[P][Q]>;
  select<
    P extends keyof CONTEXT,
    Q extends keyof CONTEXT[P],
    R extends keyof CONTEXT[P][Q]
  >(
    path: [P, Q, R],
    options?: { includeFalsy?: boolean }
  ): Observable<CONTEXT[P][Q][R]>;
  select<
    P extends keyof CONTEXT,
    Q extends keyof CONTEXT[P],
    R extends keyof CONTEXT[P][Q],
    S extends keyof CONTEXT[P][Q][R]
  >(
    path: [P, Q, R, S],
    options?: { includeFalsy?: boolean }
  ): Observable<CONTEXT[P][Q][R][S]>;
  select<
    P extends keyof CONTEXT,
    Q extends keyof CONTEXT[P],
    R extends keyof CONTEXT[P][Q],
    S extends keyof CONTEXT[P][Q][R],
    T extends keyof CONTEXT[P][Q][R][S]
  >(
    path: [P, Q, R, S, T],
    options?: { includeFalsy?: boolean }
  ): Observable<CONTEXT[P][Q][R][S][T]>;
  select(
    path: string | (string | number)[],
    options: { includeFalsy?: boolean } = {}
  ): Observable<any> {
    let result: Observable<any>;
    if (Array.isArray(path)) {
      // Pluck does not have an overload for an array that combines strings an numbers, but the function does actually support it.
      result = this.state$.pipe(pluck(...(path as any[])));
    } else {
      result = this.state$.pipe(pluck(path));
    }
    return result.pipe(
      distinctUntilChanged(isEqual),
      filter(
        (value) =>
          (value !== undefined && value !== null && !Number.isNaN(value)) ||
          (options.includeFalsy && !value)
      ),
      shareReplay({ refCount: true })
    );
  }

  /**
   * Observes the collection at the given `path`.
   * Emits an event whenever new children are added to the collection, and/or existing children are changed.
   * The collection can be either an `object` or an `array`.
   * Emits an `array` of all new and changed children.
   * Does not detect deletions.
   *
   * @param path the path of the state to observe
   */
  watch<
    S extends keyof SubType<CONTEXT, Dictionary<any>>,
    T extends CONTEXT[S]
  >(
    path: S | [S],
    options?: { includeFalsy?: boolean }
  ): Observable<T extends any[] ? T : T[keyof T][]>;
  watch<
    M extends keyof CONTEXT,
    S extends keyof SubType<CONTEXT[M], Dictionary<any>>,
    T extends CONTEXT[M][S]
  >(
    path: [M, S],
    options?: { includeFalsy?: boolean }
  ): Observable<T extends any[] ? T : T[keyof T][]>;
  watch<
    M extends keyof CONTEXT,
    N extends keyof CONTEXT[M],
    S extends keyof SubType<CONTEXT[M][N], Dictionary<any>>,
    T extends CONTEXT[M][N][S]
  >(
    path: [M, N, S],
    options?: { includeFalsy?: boolean }
  ): Observable<T extends any[] ? T : T[keyof T][]>;
  watch<
    M extends keyof CONTEXT,
    N extends keyof CONTEXT[M],
    O extends keyof CONTEXT[M][N],
    S extends keyof SubType<CONTEXT[M][N][O], Dictionary<any>>,
    T extends CONTEXT[M][N][O][S]
  >(
    path: [M, N, O, S],
    options?: { includeFalsy?: boolean }
  ): Observable<T extends any[] ? T : T[keyof T][]>;
  watch<
    M extends keyof CONTEXT,
    N extends keyof CONTEXT[M],
    O extends keyof CONTEXT[M][N],
    P extends keyof CONTEXT[M][N][O],
    S extends keyof SubType<CONTEXT[M][N][O][P], Dictionary<any>>,
    T extends CONTEXT[M][N][O][P][S]
  >(
    path: [M, N, O, P, S],
    options?: { includeFalsy?: boolean }
  ): Observable<T extends any[] ? T : T[keyof T][]>;
  watch(path: any, options: { includeFalsy?: boolean } = {}): Observable<any> {
    return this.select(path, options).pipe(
      map((state) =>
        Array.isArray(state) ? state : Object.values(state ?? {})
      ),
      pairwise(),
      map(([old, current]) =>
        old ? differenceWith(current, old, isEqual) : current
      )
    );
  }

  /**
   * Returns an observable of the complete state
   */
  get state(): Observable<CONTEXT> {
    return this.state$.asObservable();
  }

  /**
   * Returns the current state
   */
  get value(): CONTEXT {
    return this.state$.getValue();
  }

  /**
   * Dispatch an operation that manipulates the state
   * @param action The operation to dispatch
   */
  protected dispatch(action: ACTION | ResetAction): void {
    this.actions$.next(action);
  }

  /**
   * Apply the given action to the given state, resulting in a new state object that reflects the result of the operation.
   * @param state the current state
   * @param action the operation to apply
   */
  private reducer() {
    return scan((state: CONTEXT, action: ACTION | ResetAction) => {
      const next = this.reduceAction(state, action);
      if (!AbstractStore.production) {
        // Construct a debug message representing the current action
        const logMessage = action.description
          ? `${action.type}: ${action.description}`
          : action.type;

        // Log the debug message to the console
        this.logger.debug(logMessage);

        // If the user has Redux devtools enabled, also log the action there
        if (win.devTools) {
          win.devTools.send(`[${this.name}] ${logMessage}`, next);
        }
      }
      return next;
    }, this.state$.value);
  }

  private reduceAction(
    state: CONTEXT,
    action: Action<CONTEXT> | ResetAction
  ): CONTEXT {
    const rootReducer = this.rootReducers[action.type];
    return rootReducer ? (rootReducer(state, action) as CONTEXT) : state;
  }

  private reduceReset() {
    return this.defaultState;
  }
}
