import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';
import { Dictionary } from 'lodash';
import { ServicesModelModule } from './services-model.module';

export interface ModelDataStoreContext {
  readonly dataByConceptId?: Dictionary<Dictionary<any>>;
}

@Injectable({
  providedIn: ServicesModelModule,
})
export class ModelDataService extends BasicStore<ModelDataStoreContext> {
  constructor(storeService: StoreService) {
    super({ name: 'ModelDataService', storeService });
  }

  set dataByConceptId(dataByConceptId: Dictionary<Dictionary<any>>) {
    this.update({
      description: 'New model data available',
      payload: { dataByConceptId },
    });
  }
}
