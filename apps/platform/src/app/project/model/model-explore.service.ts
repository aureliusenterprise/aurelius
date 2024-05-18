import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';

export interface ModelExplorerStoreContext {
  readonly branch?: string;
  readonly version?: number;
}

@Injectable()
export class ModelExploreService extends BasicStore<ModelExplorerStoreContext> {
  constructor(storeService: StoreService) {
    super({ name: 'ModelExploreService', storeService });
  }
}
