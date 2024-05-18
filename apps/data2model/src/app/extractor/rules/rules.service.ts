import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';

export interface RulesStoreContext {
  readonly isSaveRulesModalActive?: boolean;
}

@Injectable()
export class RulesService extends BasicStore<RulesStoreContext> {
  constructor(storeService: StoreService) {
    super({ name: 'RulesService', storeService });
    this.init();
  }

  private init() {
    this.set({
      description: 'Set default state',
      payload: {
        isSaveRulesModalActive: false
      }
    });
  }
}
