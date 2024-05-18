import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import {
  AppSearchResult,
  AtlasEntitySearchObject
} from '@models4insight/atlas/api';
import { combineLatest, Observable } from 'rxjs';
import { first, map } from 'rxjs/operators';
import {
  $APP_SEARCH_DOCUMENT_PROVIDER,
  AppSearchDocumentProvider
} from '../../services/element-search/app-search-document-provider';
import { FilteredPropertiesService } from '../../services/filtered-properties/filtered-properties.service';
import { CompliantCardsComponent } from './compliant-cards/compliant-cards.component';
import { NonCompliantCardsComponent } from './non-compliant-cards/non-compliant-cards.component';

@Component({
  selector: 'models4insight-gov-quality-details',
  templateUrl: 'gov-quality-details.component.html',
  styleUrls: ['gov-quality-details.component.scss'],
})
export class GovQualityDetailsComponent implements OnInit {
  @ViewChild(CompliantCardsComponent, { static: true })
  readonly compliant: CompliantCardsComponent;

  @ViewChild(NonCompliantCardsComponent, { static: true })
  readonly nonCompliant: NonCompliantCardsComponent;

  readonly propertyCount$: Observable<number>;
  readonly searchResult$: Observable<AppSearchResult<AtlasEntitySearchObject>>;

  protected compliantCount$: Observable<number>;
  protected nonCompliantCount$: Observable<number>;
  protected govQualityScore$: Observable<number>;

  constructor(
    private readonly filteredPropertiesService: FilteredPropertiesService,
    @Inject($APP_SEARCH_DOCUMENT_PROVIDER)
    private readonly searchResultService: AppSearchDocumentProvider<AtlasEntitySearchObject>
  ) {
    this.propertyCount$ = this.filteredPropertiesService.state.pipe(
      map((properties) => Object.keys(properties).length)
    );

    this.searchResult$ = this.searchResultService.document$;
  }

  ngOnInit() {
    this.compliantCount$ = this.compliant.searchResultsService.meta$.pipe(
      first(),
      map((meta) => meta.page.total_results)
    );

    this.nonCompliantCount$ = this.nonCompliant.searchResultsService.meta$.pipe(
      first(),
      map((meta) => meta.page.total_results)
    );

    this.govQualityScore$ = combineLatest([
      this.compliantCount$,
      this.nonCompliantCount$,
    ]).pipe(
      map(
        ([compliantCount, nonCompliantCount]) =>
          (compliantCount / (compliantCount + nonCompliantCount)) * 100
      )
    );
  }
}
