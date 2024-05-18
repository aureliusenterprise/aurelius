import { Injectable } from '@angular/core';
import { AtlasEntitySearchObject } from '@models4insight/atlas/api';
import {
  EntitySearchObject,
  ENTITY_SEARCH_FACETS,
  ENTITY_SEARCH_FIELDS
} from '../../../../services/search/entity-search.service';
import { DetailsCardsSearchService } from './details-cards-search.service';

@Injectable()
export class EntityDetailsCardsSearchService extends DetailsCardsSearchService<
  AtlasEntitySearchObject,
  EntitySearchObject
> {
  constructor() {
    super({
      query: '',
      page: {
        current: 1,
        size: 5,
      },
      result_fields: ENTITY_SEARCH_FIELDS,
      facets: ENTITY_SEARCH_FACETS,
    });
  }
}
