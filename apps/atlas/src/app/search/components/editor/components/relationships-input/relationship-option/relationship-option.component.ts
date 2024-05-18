import { Component, EventEmitter, Input, Output } from '@angular/core';
import {
  AppSearchResult,
  AtlasEntitySearchObject
} from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import { $APP_SEARCH_DOCUMENT_PROVIDER } from '../../../../../services/element-search/app-search-document-provider';
import { AppSearchDocumentService } from '../../../../../services/element-search/app-search-document.service';

@Component({
  selector: 'models4insight-relationship-option',
  templateUrl: 'relationship-option.component.html',
  styleUrls: ['relationship-option.component.scss'],
  providers: [
    AppSearchDocumentService,
    {
      provide: $APP_SEARCH_DOCUMENT_PROVIDER,
      useExisting: AppSearchDocumentService,
    },
  ],
})
export class RelationshipOptionComponent {
  @Output() readonly clicked = new EventEmitter<void>();

  readonly searchResult$: Observable<AppSearchResult<AtlasEntitySearchObject>>;

  constructor(
    private readonly searchResultService: AppSearchDocumentService<AtlasEntitySearchObject>
  ) {
    this.searchResult$ = this.searchResultService.document$;
  }

  onClicked() {
    this.clicked.emit();
  }

  preventBlur(event: Event) {
    event.preventDefault();
  }

  @Input() set searchResult(
    searchResult: AppSearchResult<AtlasEntitySearchObject>
  ) {
    this.searchResultService.document = searchResult;
  }
}
