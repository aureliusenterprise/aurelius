import {
  ModuleWithProviders,
  NgModule,
  Optional,
  SkipSelf,
} from '@angular/core';
import { ProjectServiceConfig } from './services-project-config.service';

@NgModule()
export class ServicesProjectModule {
  constructor(@Optional() @SkipSelf() parentModule: ServicesProjectModule) {
    if (parentModule) {
      throw new Error(
        'ServicesProjectModule is already loaded. Import it in the AppModule only'
      );
    }
  }

  static forRoot(
    config: ProjectServiceConfig
  ): ModuleWithProviders<ServicesProjectModule> {
    return {
      ngModule: ServicesProjectModule,
      providers: [
        {
          provide: ProjectServiceConfig,
          useValue: config,
        },
      ],
    };
  }
}
