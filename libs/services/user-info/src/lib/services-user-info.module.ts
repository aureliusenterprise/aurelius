import { NgModule, Optional, SkipSelf } from '@angular/core';

@NgModule()
export class ServicesUserInfoModule {
  constructor(@Optional() @SkipSelf() parentModule: ServicesUserInfoModule) {
    if (parentModule) {
      throw new Error(
        'ServicesUserInfoModule is already loaded. Import it in the AppModule only'
      );
    }
  }
}
