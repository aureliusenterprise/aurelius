import { InjectionToken } from '@angular/core';

export interface ReduxConfig {
  readonly production?: boolean;
}
export const ReduxConfigService = new InjectionToken<ReduxConfig>(
  'ReduxConfig'
);
