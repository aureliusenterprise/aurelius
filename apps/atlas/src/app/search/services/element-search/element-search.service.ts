import { Injectable } from '@angular/core';
import {
  AppSearchDocument,
  AppSearchFilters,
  AppSearchQuery,
} from '@models4insight/atlas/api';
import { BasicStore } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { SearchService } from '../search/search.service';

export interface ElementSearchStoreContext {
  readonly guid?: string;
}

@Injectable()
export class ElementSearchService<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> extends BasicStore<ElementSearchStoreContext> {
  readonly guid$: Observable<string>;

  constructor(private readonly searchService: SearchService<T, P>) {
    super();

    this.guid$ = this.select('guid');

    this.guid$
      .pipe(
        map((guid) => this.buildQueryObject(guid)),
        untilDestroyed(this)
      )
      .subscribe((queryObject) => (this.searchService.filters = queryObject));
  }

  private buildQueryObject(guid: string): AppSearchFilters<AppSearchDocument> {
    return {
      all: [{ guid: [guid] }],
    };
  }

  set guid(guid: string) {
    this.update({
      description: 'New guid available',
      payload: { guid },
    });
  }
}
