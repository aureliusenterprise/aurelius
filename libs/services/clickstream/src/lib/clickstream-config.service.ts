import { InjectionToken } from '@angular/core';

export interface ClickstreamConfig {
  readonly app: string;
  readonly enabled: boolean;
}

export const ClickstreamConfigService = new InjectionToken<ClickstreamConfig>(
  'ClickstreamConfig'
);
