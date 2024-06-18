import {
  Inject,
  ModuleWithProviders,
  NgModule,
  Optional,
  SkipSelf,
} from '@angular/core';
import { AbstractStore } from './abstract-store';
import { ReduxConfig, ReduxConfigService } from './redux-config.service';

/*
 * Enable integration with Redux dev tools if:
 * - Running in dev mode, and
 * - The extension is available in the user's browser.
 */
const win = window as any;

const reduxDevToolsOptions = {
  maxAge: 15,
  features: {
    pause: false,
    lock: false,
    persist: false,
    jump: false,
    skip: false,
    reorder: false,
    dispatch: false,
    test: false,
  },
};

@NgModule()
export class ReduxModule {
  constructor(
    @Optional() @Inject(ReduxConfigService) config: ReduxConfig = {},
    @Optional() @SkipSelf() parentModule: ReduxModule
  ) {
    if (parentModule) {
      throw new Error(
        'ReduxModule is already loaded. Import it in the AppModule only'
      );
    }
    if (config.production) {
      AbstractStore.enableProductionMode();
    } else if (win.__REDUX_DEVTOOLS_EXTENSION__) {
      win.devTools =
        win.__REDUX_DEVTOOLS_EXTENSION__.connect(reduxDevToolsOptions);
    }
  }

  static forRoot(config: ReduxConfig = {}): ModuleWithProviders<ReduxModule> {
    return {
      ngModule: ReduxModule,
      providers: [
        {
          provide: ReduxConfigService,
          useValue: config,
        },
      ],
    };
  }
}
