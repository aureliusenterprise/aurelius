import { Injectable, OnDestroy } from '@angular/core';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { UserSearch, userSearch } from '@models4insight/repository';
import { untilDestroyed } from '@models4insight/utils';
import { debounceTime, switchMap } from 'rxjs/operators';

export interface UserSearchInputStoreContext {
  readonly isSearching?: boolean;
  readonly query?: string;
  readonly suggestions?: UserSearch[];
}

export const USER_SEARCH_DEBOUNCE_INTERVAL = 200; // ms

// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
@Injectable()
export class UserSearchInputService
  extends BasicStore<UserSearchInputStoreContext>
  implements OnDestroy
{
  constructor() {
    super();
    this.init();
  }

  ngOnDestroy() {}

  private init() {
    // Set the default state
    this.set({
      description: 'Set default state',
      payload: {
        isSearching: false,
        suggestions: [],
      },
    });

    // Whenever the query updates, retrieve a new set of suggestions.
    // Only update the search results after the user has stopped typing for a while.
    this.select('query')
      .pipe(
        debounceTime(USER_SEARCH_DEBOUNCE_INTERVAL),
        switchMap((query) => this.handleUserSearch(query)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  @MonitorAsync('isSearching')
  private async handleUserSearch(query: string) {
    // Run the query and fetch the current users
    const suggestions = await userSearch(query)
      .toPromise()
      .catch(() => []);

    // Update the store
    this.update({
      description: 'New user search suggestions available',
      payload: {
        suggestions,
      },
    });
  }
}
