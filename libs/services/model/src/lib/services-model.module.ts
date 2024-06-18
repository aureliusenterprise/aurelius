import { NgModule, Optional, SkipSelf } from '@angular/core';

@NgModule()
export class ServicesModelModule {
  constructor(@Optional() @SkipSelf() parentModule: ServicesModelModule) {
    if (parentModule) {
      throw new Error(
        'ServicesModelModule is already loaded. Import it in the AppModule only'
      );
    }
  }
}
