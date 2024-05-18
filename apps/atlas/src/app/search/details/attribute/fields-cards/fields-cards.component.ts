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
export class FieldsCardsSearchService extends EntityDetailsCardsSearchService {
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
  ): AppSearchQuery<AtlasEntitySearchObject, EntitySearchObject> {
    return {
      query: '',
      facets: {
        derivedsystem: { type: 'value', size: 100 },
        derivedcollection: { type: 'value', size: 100 },
        deriveddataset: { type: 'value', size: 100 },
      },
      page: { current: 1, size: 9 },
      result_fields: ENTITY_SEARCH_FIELDS,
      filters: {
        all: [
          { supertypenames: ['m4i_field'] },
          {
            deriveddataattributeguid: [entityId],
          },
        ],
      },
    };
  }
}

const sortingOptions: string[] = [
  'name',
  'derivedsystem',
  'derivedcollection',
  'deriveddataset',
  'dqscore_accuracy',
  'dqscore_completeness',
  'dqscore_timeliness',
  'dqscore_uniqueness',
  'dqscore_validity',
];

@Component({
  selector: 'models4insight-fields-cards',
  templateUrl: 'fields-cards.component.html',
  styleUrls: ['fields-cards.component.scss'],
  providers: [
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
    FieldsCardsSearchService,
    { provide: SearchService, useExisting: FieldsCardsSearchService },
    {
      provide: DetailsCardsSearchService,
      useExisting: FieldsCardsSearchService,
    },
  ],
})
export class FieldsCardsComponent {
  readonly sortingOptions = sortingOptions;
}
