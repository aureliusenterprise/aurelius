import { Component, Inject, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AppSearchDocument, AppSearchResult } from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import { iconsByType } from '../../meta';
import {
  $APP_SEARCH_DOCUMENT_PROVIDER,
  AppSearchDocumentProvider,
} from '../../services/element-search/app-search-document-provider';
import { Breadcrumb, BreadCrumbsService } from './bread-crumbs.service';

@Component({
  selector: 'models4insight-bread-crumbs',
  templateUrl: './bread-crumbs.component.html',
  styleUrls: ['./bread-crumbs.component.scss'],
  providers: [BreadCrumbsService],
})
export class BreadCrumbsComponent<
  T extends AppSearchDocument = AppSearchDocument
> implements OnInit
{
  readonly iconsByType = iconsByType;

  breadcrumbs$: Observable<Breadcrumb[]>;
  searchResult$: Observable<AppSearchResult<T>>;

  @Input() activeGuid: string;
  @Input() showLast = true;

  constructor(
    private readonly breadCrumbsService: BreadCrumbsService,
    private readonly router: Router,
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentProvider<T>
  ) {}

  ngOnInit() {
    this.breadcrumbs$ = this.breadCrumbsService.select('breadcrumbs', {
      includeFalsy: true,
    });
    this.searchResult$ = this.searchResultService.document$;
  }

  directToNewEntity(guid: string) {
    this.router.navigate(['search/details', guid]);
  }
}
