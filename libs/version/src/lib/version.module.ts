import {
  ModuleWithProviders,
  NgModule,
  Optional,
  SkipSelf,
} from '@angular/core';
import { VersionConfig, VersionConfigService } from './version-config.service';
import { VersionService } from './version.service';

declare var window: Window;

@NgModule()
export class VersionModule {
  constructor(
    private readonly versionService: VersionService,
    @Optional() @SkipSelf() parentModule: VersionModule
  ) {
    if (parentModule) {
      throw new Error(
        'VersionModule is already loaded. Import it in the AppModule only'
      );
    }
    this.init();
  }

  static forRoot(
    config: VersionConfig = {}
  ): ModuleWithProviders<VersionModule> {
    return {
      ngModule: VersionModule,
      providers: [
        VersionService,
        {
          provide: VersionConfigService,
          useValue: config,
        },
      ],
    };
  }

  private init() {
    /**
     * Makes the version of the application and its connected services accessible from the browser console as a function called `version()`.
     */
    if (window && !window['version']) {
      window['version'] = (forceUpdate: boolean = false) => {
        this.versionService.getVersionDescriptor(forceUpdate).then(console.dir);
        return 'Retrieving a version descriptor of the application and connected services...';
      };
    }
  }
}
