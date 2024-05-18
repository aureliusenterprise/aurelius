import { Component, Injectable } from '@angular/core';
import {
  faCheckCircle,
  faExclamationTriangle
} from '@fortawesome/free-solid-svg-icons';
import { AppSearchResult } from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { AppSearchResultsService } from '../../../../services/app-search-results/app-search-results.service';
import { GovQualitySearchResultsService } from '../../../../services/app-search-results/gov-quality-search-results.service';
import { EntityDetailsService } from '../../../../services/entity-details/entity-details.service';
import { SearchService } from '../../../../services/search/search.service';

export interface GovernanceQualityListDocument {
  readonly entity_guid: string;
  readonly guid: string;
  readonly name: string;
  readonly result: string;
  readonly compliant: string;
}

@Injectable()
export class GovernanceQualityListSearchService extends SearchService<GovernanceQualityListDocument> {
  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();

    this.entityDetailsService
      .select(['entityDetails', 'entity', 'guid'])
      .pipe(
        map((entityId) => this.createQueryObject(entityId)),
        untilDestroyed(this)
      )
      .subscribe((queryObject) => (this.queryObject = queryObject));
  }

  private createQueryObject(entityId: string) {
    return {
      result_fields: {
        entity_guid: { raw: {} },
        guid: { raw: {} },
        compliant: { raw: {} },
        name: { raw: {} },
        result: { raw: {} },
      },
      facets: {
        guid: { type: 'value', size: 100 },
      },
      page: {
        current: 1,
        size: 100,
      },
      query: '',
      filters: {
        all: [
          {
            entity_guid: [entityId],
          },
          {
            compliant: ['0'],
          },
        ],
      },
    };
  }
}

@Component({
  selector: 'models4insight-governance-quality-list',
  templateUrl: 'governance-quality-list.component.html',
  styleUrls: ['governance-quality-list.component.scss'],
  providers: [
    GovernanceQualityListSearchService,
    {
      provide: AppSearchResultsService,
      useClass: GovQualitySearchResultsService,
    },
    { provide: SearchService, useExisting: GovernanceQualityListSearchService },
  ],
})
export class GovernanceQualityListComponent {
  readonly faCheckCircle = faCheckCircle;
  readonly faExclamationTriangle = faExclamationTriangle;

  readonly nonCompliant$: Observable<
    AppSearchResult<GovernanceQualityListDocument>[]
  >;
  readonly totalNonCompliant$: Observable<number>;

  constructor(
    private readonly searchResultsService: AppSearchResultsService<GovernanceQualityListDocument>
  ) {
    this.nonCompliant$ = this.searchResultsService.allResults$;
    this.totalNonCompliant$ = this.searchResultsService.totalResults$;
  }
}
