import { Injectable } from '@angular/core';
import {
  AtlasEntitySearchObject,
  AtlasEntitySearchService,
} from '@models4insight/atlas/api';
import { SearchService } from '../search/search.service';
import { AppSearchResultsService } from './app-search-results.service';

@Injectable()
export class EntitySearchResultsService extends AppSearchResultsService<AtlasEntitySearchObject> {
  constructor(
    entitySearch: AtlasEntitySearchService,
    searchService: SearchService<AtlasEntitySearchObject>
  ) {
    super(entitySearch, searchService);
  }
}
