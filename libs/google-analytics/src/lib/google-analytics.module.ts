import {
  Inject,
  ModuleWithProviders,
  NgModule,
  Optional,
  SkipSelf,
} from '@angular/core';
import {
  GoogleAnalyticsConfig,
  GoogleAnalyticsConfigService,
} from './google-analytics-config.service';
import { GoogleAnalyticsService } from './google-analytics.service';

@NgModule({})
export class GoogleAnalyticsModule {
  constructor(
    @Inject(GoogleAnalyticsConfigService)
    config: GoogleAnalyticsConfig = {},
    googleAnalyticsService: GoogleAnalyticsService,
    @Optional() @SkipSelf() parentModule: GoogleAnalyticsModule
  ) {
    if (parentModule) {
      throw new Error(
        'GoogleAnalyticsModule is already loaded. Import it in the AppModule only'
      );
    }
    if (config.production) {
      googleAnalyticsService.init();
    }
  }

  static forRoot(
    config: GoogleAnalyticsConfig = {}
  ): ModuleWithProviders<GoogleAnalyticsModule> {
    return {
      ngModule: GoogleAnalyticsModule,
      providers: [
        GoogleAnalyticsService,
        {
          provide: GoogleAnalyticsConfigService,
          useValue: config,
        },
      ],
    };
  }
}
