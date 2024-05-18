import { Injectable } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  Resolve,
  RouterStateSnapshot
} from '@angular/router';
import { AppSearchDocument } from '@models4insight/atlas/api';
import { SearchService } from './services/search/search.service';

@Injectable()
export class QueryResolver<T extends AppSearchDocument>
  implements Resolve<string>
{
  constructor(private readonly searchService: SearchService<T>) {}

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    // The empty string here acts as a default value for the query, so that when we load the
    // page without a search term, we can still see results.

    const { query = '' } = route.queryParams;

    this.searchService.query = query;

    return query;
  }
}
