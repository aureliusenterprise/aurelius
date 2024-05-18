import { Component, Injectable } from '@angular/core';
import {
  AppSearchDocument,
  AppSearchQuery,
  DataQualitySearchObject,
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { map } from 'rxjs/operators';
import { AppSearchResultsService } from '../../../services/app-search-results/app-search-results.service';
import { DataQualitySearchResultsService } from '../../../services/app-search-results/data-quality-search-results.service';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import { SearchService } from '../../../services/search/search.service';
import { DetailsCardsSearchService } from '../../components/details-cards-list/services/details-cards-search.service';

export interface DataQualityCardsSearchObject extends AppSearchDocument {
  readonly guid: string;
  readonly name: string;
  readonly dataqualityruledescription: string;
  readonly dataqualityruledimension: string;
  readonly dqscore: number;
}

@Injectable()
export class DataQualityCardsSearchService extends DetailsCardsSearchService<
  DataQualitySearchObject,
  DataQualityCardsSearchObject
> {
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
  ): AppSearchQuery<DataQualitySearchObject, DataQualityCardsSearchObject> {
    return {
      query: '',
      facets: {
        dataqualityruledimension: { type: 'value', size: 100 },
      },
      page: { current: 1, size: 9 },
      result_fields: {
        guid: { raw: {} },
        name: { raw: {} },
        dataqualityruledescription: { raw: {} },
        dataqualityruledimension: { raw: {} },
        dqscore: {
          raw: {},
        },
      },
      filters: {
        all: [{ fieldguid: [entityId] }],
      },
    };
  }
}

const sortingOptions: string[] = [
  'name',
  'dataqualityruledimension',
  'dqscore',
];

@Component({
  selector: 'models4insight-data-quality-cards',
  templateUrl: 'data-quality-cards.component.html',
  styleUrls: ['data-quality-cards.component.scss'],
  providers: [
    {
      provide: AppSearchResultsService,
      useClass: DataQualitySearchResultsService,
    },
    DataQualityCardsSearchService,
    {
      provide: DetailsCardsSearchService,
      useExisting: DataQualityCardsSearchService,
    },
    { provide: SearchService, useExisting: DataQualityCardsSearchService },
  ],
})
export class DataQualityCardsComponent {
  readonly sortingOptions = sortingOptions;
}
