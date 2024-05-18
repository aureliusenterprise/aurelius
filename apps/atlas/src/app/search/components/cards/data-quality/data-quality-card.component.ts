import { Component, Inject, OnInit, Optional } from '@angular/core';
import {
  DataQualitySearchObject,
  ElasticSearchResult
} from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import {
  $APP_SEARCH_DOCUMENT_PROVIDER,
  AppSearchDocumentProvider
} from '../../../services/element-search/app-search-document-provider';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import { SHOW_DATA_QUALITY } from '../config';

@Component({
  selector: 'models4insight-data-quality-card',
  templateUrl: 'data-quality-card.component.html',
  styleUrls: ['data-quality-card.component.scss'],
})
export class DataQualityCardComponent implements OnInit {
  parentId$: Observable<string>;
  searchResult$: Observable<ElasticSearchResult>;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentProvider<DataQualitySearchObject>,
    @Optional() @Inject(SHOW_DATA_QUALITY) readonly showDataQuality: boolean
  ) {
    this.showDataQuality = this.showDataQuality ?? true;
  }

  ngOnInit() {
    this.parentId$ = this.entityDetailsService.parent?.select('entityId');
    this.searchResult$ = this.searchResultService.document$;
  }
}
