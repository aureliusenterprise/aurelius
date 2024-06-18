import { Dictionary } from 'lodash';
import { Observable } from 'rxjs';

/**
 * Any store should be based on a dictionary
 */
export type StoreContext = Dictionary<any>;

/**
 * A snapshot consists of a dictionary of store contexts keyed by store names
 */
export type StoreSnapshot = Dictionary<StoreContext>;

/**
 * A store provides an extensible state management framework implementing [the Redux pattern](https://medium.com/@_bengarrison/an-introduction-to-redux-ea0d91de035e).
 *
 * The `Store` does not allow its users to assign new values to the state directly.
 * Instead, users must dispatch `Actions` to the `Store`, which will update the state in the order in which the actions were dispatched. This helps keep the behavior of the application predictable.
 */
export interface Store<CONTEXT extends StoreContext> {
  readonly name: string;
  readonly state: Observable<CONTEXT>;
  readonly value: CONTEXT;
}
