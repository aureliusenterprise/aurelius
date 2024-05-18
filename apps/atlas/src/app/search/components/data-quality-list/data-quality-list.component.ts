import { Component, Inject, Input } from '@angular/core';
import {
  AppSearchResult,
  AtlasEntitySearchObject
} from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import {
  $APP_SEARCH_DOCUMENT_PROVIDER,
  AppSearchDocumentProvider
} from '../../services/element-search/app-search-document-provider';

@Component({
  selector: 'models4insight-data-quality-list',
  templateUrl: 'data-quality-list.component.html',
  styleUrls: ['data-quality-list.component.scss'],
})
export class DataQualityListComponent {
  readonly searchResult$: Observable<AppSearchResult<AtlasEntitySearchObject>>;

  @Input() showPlaceholder = true;

  constructor(
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentProvider<AtlasEntitySearchObject>
  ) {
    this.searchResult$ = this.searchResultService.document$;
  }
}
