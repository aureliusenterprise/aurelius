import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { map, mergeMap, scan } from 'rxjs/operators';
import { ReduxModule } from './redux.module';
import { Store, StoreContext, StoreSnapshot } from './store';

/**
 * This service allows stores to register themselves, enabling a snapshot which aggregates the current state of all registered stores.
 * Stores which should not be included in the snapshot, should not be registered.
 */
@Injectable({
  providedIn: ReduxModule,
})
export class StoreService {
  private register$: Subject<Store<StoreContext>> = new Subject<
    Store<StoreContext>
  >();
  private snapshot$: BehaviorSubject<StoreSnapshot> =
    new BehaviorSubject<StoreSnapshot>({});

  constructor() {
    this.init();
  }

  private init() {
    // Update the current snapshot every time the state of one of the registered stores updates
    this.register$
      .pipe(
        mergeMap((store) =>
          store.state.pipe(map((state) => ({ [store.name]: state })))
        ),
        scan(
          (snapshot, stateMap) => ({ ...snapshot, ...stateMap }),
          this.snapshot$.value
        )
      )
      .subscribe(this.snapshot$);
  }

  /** Register a store with this service */
  register(store: Store<StoreContext>) {
    this.register$.next(store);
  }

  /** Returns the current aggregated state of all registered stores */
  get snapshot(): StoreSnapshot {
    return this.snapshot$.getValue();
  }

  /** Returns an observable stream of the aggregated state of all registered stores */
  get state(): Observable<StoreSnapshot> {
    return this.snapshot$.asObservable();
  }
}
