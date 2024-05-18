import { Injectable, Optional, SkipSelf } from '@angular/core';
import {
  ElasticSearchResult,
  Facet,
  getFiltersAndResults,
} from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { switchMap } from 'rxjs/operators';

export const defaultResultFields = {
  typename: { raw: {} },
  breadcrumbguid: { raw: {} },
  breadcrumbname: { raw: {} },
  breadcrumbtype: { raw: {} },
  definition: { raw: {}, snippet: { size: 100, fallback: true } },

  deriveddataentity: {
    raw: {},
  },
  deriveddataset: { raw: {} },
  derivedsystem: { raw: {} },
  guid: { raw: {} },
  derivedperson: { raw: {} },
  id: { raw: {} },
  name: { raw: {} },
  derivedcollection: {
    raw: {},
  },
  deriveddatadomain: {
    raw: {},
  },
  deriveddataattribute: {
    raw: {},
  },
  derivedfield: {
    raw: {},
  },
  dqscore_overall: {
    raw: {},
  },
  dqscorecnt_overall: {
    raw: {},
  },
  dqscore_accuracy: {
    raw: {},
  },
  dqscorecnt_accuracy: {
    raw: {},
  },
  dqscore_completeness: {
    raw: {},
  },
  dqscorecnt_completeness: {
    raw: {},
  },
  dqscore_timeliness: {
    raw: {},
  },
  dqscorecnt_timeliness: {
    raw: {},
  },
  dqscore_uniqueness: {
    raw: {},
  },
  dqscorecnt_uniqueness: {
    raw: {},
  },
  dqscore_validity: {
    raw: {},
  },
  dqscorecnt_validity: {
    raw: {},
  },
  supertypenames: { raw: {} },
};

export const defaultQueryFacets: Dictionary<Facet> = {
  guid: { type: 'value', size: 1 },
};

export const defaultPage = {
  size: 1,
  current: 1,
};

export interface SearchResultStoreContext {
  readonly guid?: string;
  readonly isRetrievingSearchResult?: boolean;
  readonly searchResult?: ElasticSearchResult;
}

@Injectable()
export class SearchResultService extends BasicStore<SearchResultStoreContext> {
  constructor(@Optional() @SkipSelf() readonly parent: SearchResultService) {
    super();
    this.init();
  }

  protected init() {
    this.select('guid')
      .pipe(
        switchMap((guid) => this.handleRetrieveSearchResult(guid)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  set guid(guid: string) {
    this.update({
      description: 'New entity id available',
      payload: { guid },
    });
  }

  set searchResult(searchResult: ElasticSearchResult) {
    this.update({
      description: 'New search result available',
      payload: { searchResult },
    });
  }

  @ManagedTask('Retrieving the search result', { isQuiet: true })
  @MonitorAsync('isRetrievingSearchResult')
  private async handleRetrieveSearchResult(guid: string) {
    const searchResult = await getFiltersAndResults(
      '',
      defaultQueryFacets,
      defaultResultFields,
      defaultPage,
      { guid: [guid] }
    ).toPromise();

    this.searchResult = searchResult.results[0];
  }
}
