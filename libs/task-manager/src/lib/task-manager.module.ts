import { Injector, NgModule, SkipSelf, Optional } from '@angular/core';

@NgModule()
export class TaskManagerModule {
  static injector: Injector;

  constructor(
    injector: Injector,
    @Optional() @SkipSelf() parentModule: TaskManagerModule
  ) {
    if (parentModule) {
      throw new Error(
        'TaskManagerModule is already loaded. Import it in the AppModule only'
      );
    }
    TaskManagerModule.injector = injector;
  }
}
