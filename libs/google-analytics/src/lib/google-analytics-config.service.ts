import { InjectionToken } from '@angular/core';

export interface GoogleAnalyticsConfig {
  readonly production?: boolean;
  readonly measurementID?: string;
}

export const GoogleAnalyticsConfigService =
  new InjectionToken<GoogleAnalyticsConfig>('GoogleAnalyticsConfig');
