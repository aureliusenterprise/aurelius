import { Injectable } from '@angular/core';
import { AtlasEntitySearchObject } from '@models4insight/atlas/api';
import { map, shareReplay } from 'rxjs/operators';
import { AppSearchResultsService } from '../services/app-search-results/app-search-results.service';
import {
  FilterService,
  SearchFilters,
} from '../services/filter/filter.service';

const FIELD_ORDER: Array<keyof AtlasEntitySearchObject> = [
  'sourcetype',
  'supertypenames',
  'deriveddatadomain',
  'deriveddataentity',
  'derivedsystem',
  'derivedcollection',
  'deriveddataset',
  'derivedperson',
];

function sortFilterFields(filters: SearchFilters<AtlasEntitySearchObject>) {
  return Object.fromEntries(
    FIELD_ORDER.filter((key) => key in filters).map((key) => [
      key,
      filters[key],
    ])
  );
}

@Injectable()
export class ResultsFilterService extends FilterService<AtlasEntitySearchObject> {
  constructor(
    searchResultsService: AppSearchResultsService<AtlasEntitySearchObject>
  ) {
    super(searchResultsService);

    this.filters$ = this.filters$.pipe(
      map(sortFilterFields),
      shareReplay({ refCount: true })
    );
  }
}
