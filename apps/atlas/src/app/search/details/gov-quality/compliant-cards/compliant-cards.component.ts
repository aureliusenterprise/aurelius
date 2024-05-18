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

export interface CompliantEntitySearchObject extends AppSearchDocument {
  readonly entity_guid: string;
}

@Injectable()
export class CompliantEntitiesSearchService extends SearchService<
  GovQualitySearchObject,
  CompliantEntitySearchObject
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
  ): AppSearchQuery<GovQualitySearchObject, CompliantEntitySearchObject> {
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
      filters: { all: [{ compliant: ['1'] }, { guid: [entityId] }] },
    };
  }
}

@Injectable()
export class CompliantEntitiesSearchResultsService extends AppSearchResultsService<
  GovQualitySearchObject,
  CompliantEntitySearchObject
> {
  constructor(
    govQualitySearch: GovernanceQualitySearchService<CompliantEntitySearchObject>,
    compliantEntitiesSearch: CompliantEntitiesSearchService
  ) {
    super(govQualitySearch, compliantEntitiesSearch);
  }
}

@Injectable()
export class CompliantCardsSearchService extends EntityDetailsCardsSearchService {
  constructor(
    private readonly searchResultsService: CompliantEntitiesSearchResultsService
  ) {
    super();

    this.searchResultsService.allResults$
      .pipe(
        map((outputs) => this.createQueryObject(outputs)),
        untilDestroyed(this)
      )
      .subscribe((queryObject) => this.updateDefaultQueryObject(queryObject));
  }

  private createQueryObject(
    compliantEntities: AppSearchResult<CompliantEntitySearchObject>[]
  ): AppSearchQuery<AtlasEntitySearchObject, EntitySearchObject> {
    return {
      query: '',
      facets: ENTITY_SEARCH_FACETS,
      result_fields: ENTITY_SEARCH_FIELDS,
      page: { current: 1, size: 9 },
      filters: {
        all: [
          {
            guid: compliantEntities.map((entity) => entity.entity_guid.raw),
          },
        ],
      },
    };
  }
}

const sortingOptions: string[] = ['name', 'dataqualitytype'];

@Component({
  selector: 'models4insight-compliant-cards',
  templateUrl: 'compliant-cards.component.html',
  styleUrls: ['compliant-cards.component.scss'],
  providers: [
    CompliantEntitiesSearchService,
    CompliantEntitiesSearchResultsService,
    {
      provide: AppSearchResultsService,
      useClass: EntitySearchResultsService,
    },
    CompliantCardsSearchService,
    {
      provide: DetailsCardsSearchService,
      useExisting: CompliantCardsSearchService,
    },
    { provide: SearchService, useExisting: CompliantCardsSearchService },
  ],
})
export class CompliantCardsComponent {
  readonly sortingOptions = sortingOptions;

  constructor(
    readonly searchResultsService: AppSearchResultsService<AtlasEntitySearchObject>
  ) {}
}
