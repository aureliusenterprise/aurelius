import { Injectable } from '@angular/core';
import { AppSearchDocument, AppSearchResult } from '@models4insight/atlas/api';
import { BasicStore } from '@models4insight/redux';
import { Observable } from 'rxjs';
import { AppSearchDocumentProvider } from './app-search-document-provider';

@Injectable()
export class AppSearchDocumentService<T extends AppSearchDocument>
  extends BasicStore<AppSearchResult<T>>
  implements AppSearchDocumentProvider<T>
{
  readonly document$: Observable<AppSearchResult<T>>;

  constructor() {
    super();
    this.document$ = this.state;
  }

  set document(document: AppSearchResult<T>) {
    this.set({
      description: 'New document available',
      payload: document,
    });
  }
}
