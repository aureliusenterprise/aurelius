import { InjectionToken } from '@angular/core';

export interface VersionConfig {
  /**
   * The name of the application
   */
  readonly appName?: string;
  /**
   * Whether or not the application is running in production mode
   */
  readonly production?: boolean;
}

export const VersionConfigService = new InjectionToken<VersionConfig>(
  'VersionConfig'
);
