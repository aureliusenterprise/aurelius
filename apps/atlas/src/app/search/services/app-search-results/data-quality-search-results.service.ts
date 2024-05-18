import { Injectable } from '@angular/core';
import {
  DataQualitySearchObject,
  DataQualitySearchService
} from '@models4insight/atlas/api';
import { SearchService } from '../search/search.service';
import { AppSearchResultsService } from './app-search-results.service';

@Injectable()
export class DataQualitySearchResultsService extends AppSearchResultsService<DataQualitySearchObject> {
  constructor(
    dataQualitySearch: DataQualitySearchService,
    searchService: SearchService<DataQualitySearchObject>
  ) {
    super(dataQualitySearch, searchService);
  }
}
