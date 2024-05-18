import { Component, Injectable } from '@angular/core';
import {
  AppSearchQuery,
  AtlasEntityDef,
  AtlasEntitySearchObject
} from '@models4insight/atlas/api';
import { defaultIfFalsy, untilDestroyed } from '@models4insight/utils';
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
export class OutputsCardsSearchService extends EntityDetailsCardsSearchService {
  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();

    this.entityDetailsService
      .select(
        ['entityDetails', 'entity', 'relationshipAttributes', 'outputs'],
        {
          includeFalsy: true,
        }
      )
      .pipe(
        defaultIfFalsy([]),
        map((outputs) => this.createQueryObject(outputs)),
        untilDestroyed(this)
      )
      .subscribe((queryObject) => this.updateDefaultQueryObject(queryObject));
  }

  private createQueryObject(
    outputs: AtlasEntityDef[]
  ): AppSearchQuery<AtlasEntitySearchObject, EntitySearchObject> {
    return {
      query: '',
      facets: {
        typename: { type: 'value', size: 100 },
        derivedsystem: { type: 'value', size: 100 },
        derivedcollection: { type: 'value', size: 100 },
      },
      result_fields: ENTITY_SEARCH_FIELDS,
      page: { current: 1, size: 9 },
      filters: {
        all: [
          { supertypenames: ['m4i_dataset'] },
          {
            guid: outputs.map((consumer) => consumer.guid),
          },
        ],
      },
    };
  }
}

const sortingOptions: string[] = ['name'];

@Component({
  selector: 'models4insight-outputs-cards',
  templateUrl: 'outputs-cards.component.html',
  styleUrls: ['outputs-cards.component.scss'],
  providers: [
    {
      provide: AppSearchResultsService,
      useClass: EntitySearchResultsService,
    },
    OutputsCardsSearchService,
    {
      provide: DetailsCardsSearchService,
      useExisting: OutputsCardsSearchService,
    },
    { provide: SearchService, useExisting: OutputsCardsSearchService },
  ],
})
export class OutputsCardsComponent {
  readonly sortingOptions = sortingOptions;
}
