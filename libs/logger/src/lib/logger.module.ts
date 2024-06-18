import {
  Inject,
  ModuleWithProviders,
  NgModule,
  Optional,
  SkipSelf,
} from '@angular/core';
import { Logger } from './logger';
import { LoggerConfig, LoggerConfigService } from './logger-config.service';

@NgModule()
export class LoggerModule {
  constructor(
    @Optional() @Inject(LoggerConfigService) config: LoggerConfig = {},
    @Optional() @SkipSelf() parentModule: LoggerModule
  ) {
    if (parentModule) {
      throw new Error(
        'LoggerModule is already loaded. Import it in the AppModule only'
      );
    }
    if (config.production) {
      Logger.enableProductionMode();
    }
  }

  static forRoot(config: LoggerConfig = {}): ModuleWithProviders<LoggerModule> {
    return {
      ngModule: LoggerModule,
      providers: [
        {
          provide: LoggerConfigService,
          useValue: config,
        },
      ],
    };
  }
}
