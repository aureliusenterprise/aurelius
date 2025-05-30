import { Component, Injectable } from '@angular/core';
import {
  AppSearchQuery,
  AtlasEntityDef,
  AtlasEntitySearchObject,
} from '@models4insight/atlas/api';
import { defaultIfFalsy, untilDestroyed } from '@models4insight/utils';
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
export class ProducersCardsSearchService extends EntityDetailsCardsSearchService {
  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();

    this.entityDetailsService
      .select(
        [
          'entityDetails',
          'entity',
          'relationshipAttributes',
          'outputFromProcesses',
        ],
        { includeFalsy: true }
      )
      .pipe(
        defaultIfFalsy([]),
        map((producers) => this.createQueryObject(producers)),
        untilDestroyed(this)
      )
      .subscribe((queryObject) => this.updateDefaultQueryObject(queryObject));
  }

  private createQueryObject(
    producers: AtlasEntityDef[]
  ): AppSearchQuery<AtlasEntitySearchObject, EntitySearchObject> {
    return {
      query: '',
      facets: {
        typename: { type: 'value', size: 100 },
        derivedsystem: { type: 'value', size: 100 },
      },
      result_fields: ENTITY_SEARCH_FIELDS,
      page: { current: 1, size: 9 },
      filters: {
        all: [
          { supertypenames: ['m4i_generic_process'] },
          {
            guid: producers.map((consumer) => consumer.guid),
          },
        ],
      },
    };
  }
}

const sortingOptions: string[] = ['name'];

@Component({
  selector: 'models4insight-producers-cards',
  templateUrl: 'producers-cards.component.html',
  styleUrls: ['producers-cards.component.scss'],
  providers: [
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
    ProducersCardsSearchService,
    {
      provide: DetailsCardsSearchService,
      useExisting: ProducersCardsSearchService,
    },
    { provide: SearchService, useExisting: ProducersCardsSearchService },
  ],
})
export class ProducersCardsComponent {
  readonly sortingOptions = sortingOptions;
}
