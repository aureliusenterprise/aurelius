import { NgModule, Optional, SkipSelf } from '@angular/core';

@NgModule()
export class ServicesBranchModule {
  constructor(@Optional() @SkipSelf() parentModule: ServicesBranchModule) {
    if (parentModule) {
      throw new Error(
        'ServicesBranchModule is already loaded. Import it in the AppModule only'
      );
    }
  }
}
