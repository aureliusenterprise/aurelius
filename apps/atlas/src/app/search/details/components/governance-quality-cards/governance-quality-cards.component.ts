import { Component, Injectable } from '@angular/core';
import {
  AppSearchQuery,
  GovQualitySearchObject,
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { map } from 'rxjs/operators';
import { AppSearchResultsService } from '../../../services/app-search-results/app-search-results.service';
import { GovQualitySearchResultsService } from '../../../services/app-search-results/gov-quality-search-results.service';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import { SearchService } from '../../../services/search/search.service';
import { DetailsCardsSearchService } from '../details-cards-list/services/details-cards-search.service';

@Injectable()
export class GovernanceQualityCardsSearchService extends DetailsCardsSearchService<GovQualitySearchObject> {
  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();

    this.entityDetailsService
      .select('entityId')
      .pipe(
        map((entityId) => this.createQueryObject(entityId)),
        untilDestroyed(this)
      )
      .subscribe((queryObject) => this.updateDefaultQueryObject(queryObject));
  }

  private createQueryObject(
    entityId: string
  ): AppSearchQuery<GovQualitySearchObject> {
    return {
      query: '',
      facets: {
        dataqualityruledimension: { type: 'value', size: 100 },
        dataqualitytype: { type: 'value', size: 100 },
      },
      page: { current: 1, size: 9 },
      filters: {
        all: [{ entity_guid: [entityId] }],
      },
    };
  }
}

const sortingOptions: string[] = [
  'name',
  'dataqualityruledimension',
  'compliant',
];

@Component({
  selector: 'models4insight-governance-quality-cards',
  templateUrl: 'governance-quality-cards.component.html',
  styleUrls: ['governance-quality-cards.component.scss'],
  providers: [
    {
      provide: AppSearchResultsService,
      useClass: GovQualitySearchResultsService,
    },
    GovernanceQualityCardsSearchService,
    {
      provide: SearchService,
      useExisting: GovernanceQualityCardsSearchService,
    },
    {
      provide: DetailsCardsSearchService,
      useExisting: GovernanceQualityCardsSearchService,
    },
  ],
})
export class GovernanceQualityCardsComponent {
  readonly sortingOptions = sortingOptions;
}
