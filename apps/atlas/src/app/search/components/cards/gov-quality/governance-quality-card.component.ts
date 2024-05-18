import { Component, Inject, OnInit } from '@angular/core';
import {
  faCheckCircle,
  faExclamationTriangle
} from '@fortawesome/free-solid-svg-icons';
import {
  AppSearchResult, GovQualitySearchObject
} from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import {
  $APP_SEARCH_DOCUMENT_PROVIDER,
  AppSearchDocumentProvider
} from '../../../services/element-search/app-search-document-provider';

@Component({
  selector: 'models4insight-governance-quality-card',
  templateUrl: 'governance-quality-card.component.html',
  styleUrls: ['governance-quality-card.component.scss'],
})
export class GovernanceQualityCardComponent implements OnInit {
  readonly faCheckCircle = faCheckCircle;
  readonly faExclamationTriangle = faExclamationTriangle;

  searchResult$: Observable<AppSearchResult<GovQualitySearchObject>>;

  constructor(
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentProvider<GovQualitySearchObject>
  ) {}

  ngOnInit() {
    this.searchResult$ = this.searchResultService.document$;
  }
}
