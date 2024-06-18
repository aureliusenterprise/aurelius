import { Injector, ModuleWithProviders, NgModule } from '@angular/core';
import { HttpCacheService, HttpService } from '@models4insight/http';
import { AppSearchClient, APP_SEARCH_TOKEN } from './app-search-client.service';
import { AtlasEntitySearchService } from './engines/atlas-entity-search.service';
import { DataQualitySearchService } from './engines/data-quality-search.service';
import { GovernanceQualitySearchService } from './engines/gov-quality-search.service';

export interface ElasticApiConfig {
  readonly appSearchToken?: string;
}

export function getHttpClient(): HttpService {
  if (!ElasticApiModule.injector) {
    throw new Error(
      'Tried running an API query while the ElasticApiModule was not loaded. Please make sure the ElasticApiModule is imported.'
    );
  }
  return ElasticApiModule.injector.get(AppSearchClient) as HttpService;
}

export function getHttpCache(): HttpCacheService {
  if (!ElasticApiModule.injector) {
    throw new Error(
      'Tried accessing the cache while the ElasticApiModule was not loaded. Please make sure the ElasticApiModule is imported.'
    );
  }
  return ElasticApiModule.injector.get(HttpCacheService);
}

@NgModule({
  providers: [
    AppSearchClient,
    AtlasEntitySearchService,
    DataQualitySearchService,
    GovernanceQualitySearchService,
  ],
})
export class ElasticApiModule {
  static injector: Injector;

  constructor(injector: Injector) {
    ElasticApiModule.injector = injector;
  }

  static forRoot(
    config: ElasticApiConfig = {}
  ): ModuleWithProviders<ElasticApiModule> {
    return {
      ngModule: ElasticApiModule,
      providers: [
        {
          provide: APP_SEARCH_TOKEN,
          useValue: config.appSearchToken,
        },
      ],
    };
  }
}
