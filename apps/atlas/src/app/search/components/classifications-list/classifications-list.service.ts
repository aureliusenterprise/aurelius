import { Injectable } from '@angular/core';
import { Classification } from '@models4insight/atlas/api';
import { BasicStore } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';

@Injectable()
export class ClassificationsListService extends BasicStore<
  Dictionary<string[]>
> {
  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();
    this.init();
  }

  private init() {
    this.entityDetailsService.entityDetails$
      .pipe(untilDestroyed(this))
      .subscribe((entity) =>
        this.handleGroupClassifictionsByTypeName(entity.classifications)
      );
  }

  private handleGroupClassifictionsByTypeName(
    classifications: Classification[] = []
  ) {
    const result: Dictionary<string[]> = {};

    for (const { typeName, entityGuid } of classifications) {
      if (!(typeName in result)) {
        result[typeName] = [];
      }
      result[typeName].push(entityGuid);
    }

    this.set({
      description: 'New classifications by type name available',
      payload: result,
    });
  }
}
