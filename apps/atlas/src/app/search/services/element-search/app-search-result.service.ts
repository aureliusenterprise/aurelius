import { Injectable } from '@angular/core';
import { AppSearchDocument, AppSearchResult } from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { AppSearchResultsService } from '../app-search-results/app-search-results.service';
import { AppSearchDocumentProvider } from './app-search-document-provider';

@Injectable()
export class AppSearchResultService<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> implements AppSearchDocumentProvider<P>
{
  readonly document$: Observable<AppSearchResult<P>>;
  readonly isLoading$: Observable<boolean>;

  constructor(
    private readonly searchResultsService: AppSearchResultsService<T, P>
  ) {
    this.document$ = this.searchResultsService.results$.pipe(
      map((results) => results[0])
    );
    this.isLoading$ = this.searchResultsService.isLoadingPage$;
  }
}
