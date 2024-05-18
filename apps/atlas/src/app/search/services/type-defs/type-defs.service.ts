import { Injectable } from '@angular/core';
import {
  AtlasEntityDef,
  AtlasTypesDef, TypeDefAPIService
} from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { indexByProperty, untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';

export interface TypeDefsStoreContext {
  readonly entityTypesByName?: Dictionary<AtlasEntityDef>;
  readonly isRetrievingTypeDefs?: boolean;
  readonly typeDefs?: AtlasTypesDef;
}

@Injectable({ providedIn: 'root' })
export class TypeDefsService extends BasicStore<TypeDefsStoreContext> {
  constructor(private readonly typeDefApiService: TypeDefAPIService) {
    super();
    this.init();
  }

  private init() {
    this.handleRetrieveTypeDefs();

    this.select('typeDefs')
      .pipe(untilDestroyed(this))
      .subscribe((typeDefs) => this.handleIndexEntityTypes(typeDefs));
  }

  @ManagedTask('Retrieving the type definitions', { isQuiet: true })
  @MonitorAsync('isRetrievingTypeDefs')
  private async handleRetrieveTypeDefs() {
    const typeDefs = await this.typeDefApiService.getTypeDefs().toPromise();
    this.update({
      description: 'New type defs available',
      payload: { typeDefs },
    });
  }

  private handleIndexEntityTypes(typeDefs: AtlasTypesDef) {
    const entityTypesByName = indexByProperty(typeDefs.entityDefs, 'name');

    this.update({
      description: 'Entity types by name index updated',
      payload: { entityTypesByName },
    });
  }
}
