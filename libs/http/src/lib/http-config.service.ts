import { InjectionToken } from '@angular/core';

export interface HttpConfig {
  production?: boolean;
}

export const HttpConfigService = new InjectionToken<HttpConfig>('HttpConfig');
