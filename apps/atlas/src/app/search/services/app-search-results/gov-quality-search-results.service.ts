import { Injectable } from '@angular/core';
import {
  GovernanceQualitySearchService,
  GovQualitySearchObject
} from '@models4insight/atlas/api';
import { SearchService } from '../search/search.service';
import { AppSearchResultsService } from './app-search-results.service';

@Injectable()
export class GovQualitySearchResultsService extends AppSearchResultsService<GovQualitySearchObject> {
  constructor(
    govQualitySearch: GovernanceQualitySearchService,
    searchService: SearchService<GovQualitySearchObject>
  ) {
    super(govQualitySearch, searchService);
  }
}
