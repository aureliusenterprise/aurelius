import { Component, Injectable } from '@angular/core';
import {
  AppSearchQuery,
  AtlasEntitySearchObject,
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { map } from 'rxjs/operators';
import { AppSearchResultsService } from '../../../services/app-search-results/app-search-results.service';
import { EntitySearchResultsService } from '../../../services/app-search-results/entity-search-results.service';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import {
  EntitySearchObject,
  ENTITY_SEARCH_FIELDS,
} from '../../../services/search/entity-search.service';
import { SearchService } from '../../../services/search/search.service';
import { DetailsCardsSearchService } from '../../components/details-cards-list/services/details-cards-search.service';
import { EntityDetailsCardsSearchService } from '../../components/details-cards-list/services/entity-details-cards-search.service';

@Injectable()
export class GovernanceRolesCardsSearchService extends EntityDetailsCardsSearchService {
  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();

    this.entityDetailsService
      .select(['entityDetails', 'entity', 'attributes', 'name'])
      .pipe(
        map((entityId) => this.createQueryObject(entityId)),
        untilDestroyed(this)
      )
      .subscribe((queryObject) => this.updateDefaultQueryObject(queryObject));
  }

  private createQueryObject(
    personName: string
  ): AppSearchQuery<AtlasEntitySearchObject, EntitySearchObject> {
    return {
      query: '',
      facets: {
        typename: { type: 'value', size: 100 },
        deriveddatadomain: { type: 'value', size: 100 },
        deriveddataentity: { type: 'value', size: 100 },
        name: { type: 'value', size: 100 },
      },
      result_fields: ENTITY_SEARCH_FIELDS,
      page: { current: 1, size: 9 },
      filters: {
        all: [
          {
            derivedperson: [personName],
          },
        ],
      },
    };
  }
}

const sortingOptions: string[] = [
  'typename',
  'deriveddatadomain',
  'deriveddataentity',
  'name',
  'dqscore_accuracy',
  'dqscore_completeness',
  'dqscore_timeliness',
  'dqscore_uniqueness',
  'dqscore_validity',
];

@Component({
  selector: 'models4insight-governance-roles-cards',
  templateUrl: 'governance-roles-cards.component.html',
  styleUrls: ['governance-roles-cards.component.scss'],
  providers: [
    {
      provide: AppSearchResultsService,
      useClass: EntitySearchResultsService,
    },
    GovernanceRolesCardsSearchService,
    {
      provide: DetailsCardsSearchService,
      useExisting: GovernanceRolesCardsSearchService,
    },
    { provide: SearchService, useExisting: GovernanceRolesCardsSearchService },
  ],
})
export class GovernanceRolesCardsComponent {
  readonly sortingOptions = sortingOptions;

  constructor(readonly searchService: SearchService<AtlasEntitySearchObject>) {}
}
