import { InjectionToken } from '@angular/core';

export interface LoggerConfig {
  readonly production?: boolean;
}

export const LoggerConfigService = new InjectionToken<LoggerConfig>(
  'LoggerConfig'
);
