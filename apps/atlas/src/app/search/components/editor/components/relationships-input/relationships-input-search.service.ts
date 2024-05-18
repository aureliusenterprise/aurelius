import { Injectable } from '@angular/core';
import {
  AppSearchFilters,
  AtlasEntitySearchObject
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest } from 'rxjs';
import { map } from 'rxjs/operators';
import { EntityDetailsService } from '../../../../services/entity-details/entity-details.service';
import { EntitySearchService } from '../../../../services/search/entity-search.service';
import { RelationshipsInputService } from './relationships-input.service';

@Injectable()
export class RelationshipsInputSearchService extends EntitySearchService {
  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly relationshipsInputService: RelationshipsInputService
  ) {
    super();

    combineLatest([
      this.entityDetailsService.select(['entityDetails', 'entity', 'guid']),
      this.relationshipsInputService.relationships$,
      this.relationshipsInputService.typeName$,
    ])
      .pipe(
        map(([entityId, currentRelations, typeName]) =>
          this.createFilterObject(entityId, currentRelations, typeName)
        ),
        untilDestroyed(this)
      )
      .subscribe((filters) => (this.filters = filters));
  }

  private createFilterObject(
    entityId: string,
    currentRelations: string[],
    typeName: string
  ): AppSearchFilters<AtlasEntitySearchObject> {
    return {
      all: [
        {
          all: [{ supertypenames: [typeName] }],
          none: [{ guid: [entityId, ...currentRelations] }],
        },
      ],
    };
  }
}
