import { InjectionToken } from '@angular/core';

export interface AuthenticationConfigCredentials {
  readonly secret: string;
}

export interface AuthenticationConfig {
  readonly clientId: string;
  readonly realm: string;
  readonly url: string;
  readonly credentials?: AuthenticationConfigCredentials;
}

export const AuthenticationConfigService =
  new InjectionToken<AuthenticationConfig>('AuthenticationConfig');
