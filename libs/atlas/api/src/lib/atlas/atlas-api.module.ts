import { Injector, NgModule } from '@angular/core';
import {
  HttpCacheService,
  HttpModule,
  HttpService,
} from '@models4insight/http';
import { AtlasApiClient } from './atlas-api-client.service';
import { ClassificationDefAPIService } from './classification-def-api.service';
import { EntityAPIService } from './entity-api.service';
import { TypeDefAPIService } from './type-def-api.service';

export function getHttpClient(): HttpService {
  if (!AtlasApiModule.injector) {
    throw new Error(
      'Tried running an API query while the AtlasApiModule was not loaded. Please make sure the AtlasApiModule is imported.'
    );
  }
  return AtlasApiModule.injector.get(AtlasApiClient) as HttpService;
}

export function getHttpCache(): HttpCacheService {
  if (!AtlasApiModule.injector) {
    throw new Error(
      'Tried accessing the cache while the AtlasApiModule was not loaded. Please make sure the AtlasApiModule is imported.'
    );
  }
  return AtlasApiModule.injector.get(HttpCacheService);
}

@NgModule({
  imports: [HttpModule.forChild()],
  providers: [
    AtlasApiClient,
    ClassificationDefAPIService,
    EntityAPIService,
    TypeDefAPIService,
  ],
})
export class AtlasApiModule {
  static injector: Injector;

  constructor(injector: Injector) {
    AtlasApiModule.injector = injector;
  }
}
