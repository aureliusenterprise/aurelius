import { Component, Injectable } from '@angular/core';
import {
  AppSearchDocument,
  AppSearchQuery,
  AppSearchResult,
  AtlasEntitySearchObject,
  GovernanceQualitySearchService,
  GovQualitySearchObject
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { map } from 'rxjs/operators';
import { AppSearchResultsService } from '../../../services/app-search-results/app-search-results.service';
import { EntitySearchResultsService } from '../../../services/app-search-results/entity-search-results.service';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import {
  EntitySearchObject,
  ENTITY_SEARCH_FACETS,
  ENTITY_SEARCH_FIELDS
} from '../../../services/search/entity-search.service';
import { SearchService } from '../../../services/search/search.service';
import { DetailsCardsSearchService } from '../../components/details-cards-list/services/details-cards-search.service';
import { EntityDetailsCardsSearchService } from '../../components/details-cards-list/services/entity-details-cards-search.service';

export interface NonCompliantEntitySearchObject extends AppSearchDocument {
  readonly entity_guid: string;
}

@Injectable()
export class NonCompliantEntitiesSearchService extends SearchService<
  GovQualitySearchObject,
  NonCompliantEntitySearchObject
> {
  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();

    this.entityDetailsService
      .select('entityId')
      .pipe(untilDestroyed(this))
      .subscribe(
        (entityId) => (this.queryObject = this.createQueryObject(entityId))
      );
  }

  private createQueryObject(
    entityId: string
  ): AppSearchQuery<GovQualitySearchObject, NonCompliantEntitySearchObject> {
    return {
      facets: {
        guid: { type: 'value', size: 100 },
      },
      page: {
        current: 0,
        size: 100,
      },
      query: '',
      result_fields: { entity_guid: { raw: {} } },
      filters: { all: [{ compliant: ['0'] }, { guid: [entityId] }] },
    };
  }
}

@Injectable()
export class NonCompliantEntitiesSearchResultsService extends AppSearchResultsService<
  GovQualitySearchObject,
  NonCompliantEntitySearchObject
> {
  constructor(
    govQualitySearch: GovernanceQualitySearchService<NonCompliantEntitySearchObject>,
    compliantEntitiesSearch: NonCompliantEntitiesSearchService
  ) {
    super(govQualitySearch, compliantEntitiesSearch);
  }
}

@Injectable()
export class NonCompliantCardsSearchService extends EntityDetailsCardsSearchService {
  constructor(
    private readonly searchResultService: NonCompliantEntitiesSearchResultsService
  ) {
    super();

    this.searchResultService.allResults$
      .pipe(
        map((outputs) => this.createQueryObject(outputs)),
        untilDestroyed(this)
      )
      .subscribe((queryObject) => this.updateDefaultQueryObject(queryObject));
  }

  private createQueryObject(
    nonCompliantEntities: AppSearchResult<NonCompliantEntitySearchObject>[]
  ): AppSearchQuery<AtlasEntitySearchObject, EntitySearchObject> {
    return {
      query: '',
      facets: ENTITY_SEARCH_FACETS,
      result_fields: ENTITY_SEARCH_FIELDS,
      page: { current: 1, size: 9 },
      filters: {
        all: [
          {
            guid: nonCompliantEntities.map((entity) => entity.entity_guid.raw),
          },
        ],
      },
    };
  }
}

const sortingOptions: string[] = ['name', 'dataqualitytype'];

@Component({
  selector: 'models4insight-non-compliant-cards',
  templateUrl: 'non-compliant-cards.component.html',
  styleUrls: ['non-compliant-cards.component.scss'],
  providers: [
    NonCompliantEntitiesSearchService,
    NonCompliantEntitiesSearchResultsService,
    {
      provide: AppSearchResultsService,
      useClass: EntitySearchResultsService,
    },
    NonCompliantCardsSearchService,
    {
      provide: DetailsCardsSearchService,
      useExisting: NonCompliantCardsSearchService,
    },
    { provide: SearchService, useExisting: NonCompliantCardsSearchService },
  ],
})
export class NonCompliantCardsComponent {
  readonly sortingOptions = sortingOptions;

  constructor(
    readonly searchResultsService: AppSearchResultsService<AtlasEntitySearchObject>
  ) {}
}
