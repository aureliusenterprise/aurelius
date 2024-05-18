import { Injectable } from '@angular/core';
import {
  AppSearchQuery, GovQualitySearchObject
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import { SearchService } from '../../../services/search/search.service';
@Injectable()
export class EditorGovQualitySearchService extends SearchService<GovQualitySearchObject> {
  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();

    this.entityDetailsService
      .select(['entityDetails', 'entity', 'guid'])
      .pipe(untilDestroyed(this))
      .subscribe(
        (entityId) => (this.queryObject = this.createQueryObject(entityId))
      );
  }

  private createQueryObject(
    entityId: string
  ): AppSearchQuery<GovQualitySearchObject> {
    return {
      query: '',
      page: {
        current: 1,
        size: 100,
      },
      facets: {
        guid: { type: 'value', size: 100 },
      },
      filters: {
        all: [
          {
            entity_guid: [entityId],
          },
        ],
      },
    };
  }
}
