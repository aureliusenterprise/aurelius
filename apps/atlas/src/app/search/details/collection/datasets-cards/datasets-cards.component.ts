import { Component, Injectable } from '@angular/core';
import {
  AppSearchQuery,
  AtlasEntitySearchObject,
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest } from 'rxjs';
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

@Injectable()
export class DatasetsCardsSearchService extends EntityDetailsCardsSearchService {
  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly showDescendantsService: ShowDescendantsService
  ) {
    super();

    combineLatest([
      this.entityDetailsService.select('entityId'),
      this.showDescendantsService.showDescendants$,
    ])
      .pipe(
        map(([entityId, showDescendants]) =>
          this.createQueryObject(entityId, showDescendants)
        ),
        untilDestroyed(this)
      )
      .subscribe((queryObject) => this.updateDefaultQueryObject(queryObject));
  }

  private createQueryObject(
    entityId: string,
    showDescendants = false
  ): AppSearchQuery<AtlasEntitySearchObject, EntitySearchObject> {
    return {
      query: '',
      facets: { derivedperson: { type: 'value', size: 100 } },
      page: { current: 1, size: 9 },
      result_fields: ENTITY_SEARCH_FIELDS,
      filters: {
        all: [
          { supertypenames: ['m4i_dataset'] },
          {
            [showDescendants ? 'derivedcollectionguid' : 'parentguid']: [
              entityId,
            ],
          },
        ],
      },
    };
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
  selector: 'models4insight-datasets-cards',
  templateUrl: 'datasets-cards.component.html',
  styleUrls: ['datasets-cards.component.scss'],
  providers: [
    { provide: AppSearchResultsService, useClass: EntitySearchResultsService },
    DatasetsCardsSearchService,
    { provide: SearchService, useExisting: DatasetsCardsSearchService },
    {
      provide: DetailsCardsSearchService,
      useExisting: DatasetsCardsSearchService,
    },
    ShowDescendantsService,
  ],
})
export class DatasetsCardsComponent {
  readonly sortingOptions = sortingOptions;
}
