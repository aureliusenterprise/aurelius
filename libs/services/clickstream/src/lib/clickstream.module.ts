import {
  ModuleWithProviders,
  NgModule,
  Optional,
  SkipSelf,
} from '@angular/core';
import {
  ClickstreamConfig,
  ClickstreamConfigService,
} from './clickstream-config.service';
import { ClickstreamService } from './clickstream.service';

@NgModule()
export class ClickstreamModule {
  constructor(
    clickstreamService: ClickstreamService,
    @Optional() @SkipSelf() parentModule: ClickstreamModule
  ) {
    if (parentModule) {
      throw new Error(
        'ClickstreamModule is already loaded. Import it in the AppModule only'
      );
    }
    clickstreamService.init();
  }

  static forRoot(
    config: ClickstreamConfig
  ): ModuleWithProviders<ClickstreamModule> {
    return {
      ngModule: ClickstreamModule,
      providers: [
        ClickstreamService,
        {
          provide: ClickstreamConfigService,
          useValue: config,
        },
      ],
    };
  }
}
