import { Component, Injectable } from '@angular/core';
import {
  AppSearchQuery,
  AtlasEntitySearchObject
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { map } from 'rxjs/operators';
import { AppSearchResultsService } from '../../../services/app-search-results/app-search-results.service';
import { EntitySearchResultsService } from '../../../services/app-search-results/entity-search-results.service';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import {
  EntitySearchObject,
  ENTITY_SEARCH_FIELDS
} from '../../../services/search/entity-search.service';
import { SearchService } from '../../../services/search/search.service';
import { DetailsCardsSearchService } from '../../components/details-cards-list/services/details-cards-search.service';
import { EntityDetailsCardsSearchService } from '../../components/details-cards-list/services/entity-details-cards-search.service';

@Injectable()
export class AttributesCardsSearchService extends EntityDetailsCardsSearchService {
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
        deriveddatadomain: { type: 'value', size: 100 },
        deriveddataentity: { type: 'value', size: 100 },
        derivedperson: { type: 'value', size: 100 },
      },
      result_fields: ENTITY_SEARCH_FIELDS,
      page: { current: 1, size: 9 },
      filters: {
        all: [
          { supertypenames: ['m4i_data_attribute'] },
          {
            derivedfieldguid: [entityId],
          },
        ],
      },
    };
  }
}

const sortingOptions: string[] = [
  'name',
  'deriveddatadomain',
  'deriveddataentity',
];

@Component({
  selector: 'models4insight-attributes-cards',
  templateUrl: 'attributes-cards.component.html',
  styleUrls: ['attributes-cards.component.scss'],
  providers: [
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
    AttributesCardsSearchService,
    {
      provide: DetailsCardsSearchService,
      useExisting: AttributesCardsSearchService,
    },
    { provide: SearchService, useExisting: AttributesCardsSearchService },
  ],
})
export class AttributesCardsComponent {
  readonly sortingOptions = sortingOptions;
}
