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
import { ShowDescendantsService } from '../../components/details-cards-list/show-descendants-control.directive';

/** A guid no entity has: an empty relationship shows no cards (an empty filter would show every entity). */
const NO_ENTITY = 'no-related-entity';

interface RelatedEntity {
  guid?: string;
  relationshipStatus?: string;
}

/**
 * Cards of the data entities related to the current entity through one relationship attribute of the "uses"
 * relationship (m4i_data_entity_usage): `uses` (the entities this entity uses) or `usedBy` (the entities that use
 * this entity).
 */
abstract class UsageCardsSearchService extends EntityDetailsCardsSearchService {
  constructor(
    entityDetailsService: EntityDetailsService,
    relationshipAttribute: 'uses' | 'usedBy'
  ) {
    super();

    entityDetailsService
      .select([
        'entityDetails',
        'entity',
        'relationshipAttributes',
        relationshipAttribute,
      ] as any)
      .pipe(
        map((related: RelatedEntity[]) =>
          (related ?? [])
            .filter(
              (entity) =>
                entity?.guid && entity.relationshipStatus !== 'DELETED'
            )
            .map((entity) => entity.guid)
        ),
        map((guids) => this.createQueryObject(guids)),
        untilDestroyed(this)
      )
      .subscribe((queryObject) => this.updateDefaultQueryObject(queryObject));
  }

  private createQueryObject(
    guids: string[]
  ): AppSearchQuery<AtlasEntitySearchObject, EntitySearchObject> {
    return {
      query: '',
      facets: { derivedperson: { type: 'value', size: 100 } },
      page: { current: 1, size: 9 },
      result_fields: ENTITY_SEARCH_FIELDS,
      filters: {
        all: [
          { supertypenames: ['m4i_data_entity'] },
          { guid: guids.length ? guids : [NO_ENTITY] },
        ],
      },
    };
  }
}

@Injectable()
export class UsesCardsSearchService extends UsageCardsSearchService {
  constructor(entityDetailsService: EntityDetailsService) {
    super(entityDetailsService, 'uses');
  }
}

@Injectable()
export class UsedByCardsSearchService extends UsageCardsSearchService {
  constructor(entityDetailsService: EntityDetailsService) {
    super(entityDetailsService, 'usedBy');
  }
}

const sortingOptions: string[] = [
  'name',
  'dqscore_accuracy',
  'dqscore_completeness',
  'dqscore_timeliness',
  'dqscore_uniqueness',
  'dqscore_validity',
];

@Component({
  selector: 'models4insight-uses-cards',
  templateUrl: 'uses-cards.component.html',
  providers: [
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
    UsesCardsSearchService,
    { provide: DetailsCardsSearchService, useExisting: UsesCardsSearchService },
    { provide: SearchService, useExisting: UsesCardsSearchService },
    ShowDescendantsService,
  ],
})
export class UsesCardsComponent {
  readonly sortingOptions = sortingOptions;
}

@Component({
  selector: 'models4insight-used-by-cards',
  templateUrl: 'used-by-cards.component.html',
  providers: [
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
    UsedByCardsSearchService,
    {
      provide: DetailsCardsSearchService,
      useExisting: UsedByCardsSearchService,
    },
    { provide: SearchService, useExisting: UsedByCardsSearchService },
    ShowDescendantsService,
  ],
})
export class UsedByCardsComponent {
  readonly sortingOptions = sortingOptions;
}
