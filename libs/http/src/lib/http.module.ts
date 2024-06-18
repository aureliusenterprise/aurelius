import { HttpClient, HttpClientModule } from '@angular/common/http';
import { ModuleWithProviders, NgModule } from '@angular/core';
import { AuthorizationHeaderInterceptor } from './authorization-header.interceptor';
import { CacheInterceptor } from './cache.interceptor';
import { ErrorHandlerInterceptor } from './error-handler.interceptor';
import { HttpCacheService } from './http-cache.service';
import { HttpConfig, HttpConfigService } from './http-config.service';
import { HttpService } from './http.service';
import { IECacheHeaderInterceptor } from './ie-cache-header-interceptor';

@NgModule({
  imports: [HttpClientModule],
})
export class HttpModule {
  constructor() {}

  static forRoot(config: HttpConfig = {}): ModuleWithProviders<HttpModule> {
    return {
      ngModule: HttpModule,
      providers: [
        {
          provide: HttpConfigService,
          useValue: config,
        },
      ],
    };
  }

  static forChild(): ModuleWithProviders<HttpModule> {
    return {
      ngModule: HttpModule,
      providers: [
        AuthorizationHeaderInterceptor,
        CacheInterceptor,
        ErrorHandlerInterceptor,
        IECacheHeaderInterceptor,
        HttpCacheService,
        {
          provide: HttpClient,
          useClass: HttpService,
        },
      ],
    };
  }
}
