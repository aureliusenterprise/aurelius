import { InjectionToken } from '@angular/core';
import { AppSearchDocument, AppSearchResult } from '@models4insight/atlas/api';
import { Observable } from 'rxjs';

export interface AppSearchDocumentProvider<
  T extends AppSearchDocument = AppSearchDocument
> {
  readonly document$: Observable<AppSearchResult<T>>;
}

export const $APP_SEARCH_DOCUMENT_PROVIDER =
  new InjectionToken<AppSearchDocumentProvider>('AppSearchDocumentProvider');
