import { Inject, Injectable } from '@angular/core';
import { Logger } from '@models4insight/logger';
import Keycloak from 'keycloak-js';
import { Observable, ReplaySubject, Subject } from 'rxjs';
import { distinctUntilChanged } from 'rxjs/operators';
import {
  AuthenticationConfig,
  AuthenticationConfigService,
} from './authentication-config.service';
import { AuthenticationModule } from './authentication.module';

const log = new Logger('KeycloakService');

export interface LoginOptions {
  action?: 'register';
  locale?: string;
  loginHint?: string;
  prompt?: 'login' | 'none';
  redirectUri?: string;
}

@Injectable({
  providedIn: AuthenticationModule,
})
export class KeycloakService {
  private readonly keycloakAuth: Keycloak.KeycloakInstance;
  private readonly authState: Subject<boolean> = new ReplaySubject<boolean>();

  constructor(
    @Inject(AuthenticationConfigService) config: AuthenticationConfig
  ) {
    this.keycloakAuth = Keycloak(config);

    this.authState.subscribe((auth: boolean) =>
      log.debug(`Auth state updated: ${auth}`)
    );

    this.keycloakAuth.onReady = (auth) => this.authState.next(auth);
    this.keycloakAuth.onAuthSuccess = () => this.authState.next(true);
    this.keycloakAuth.onAuthLogout = () => this.authState.next(false);

    /**
     * Whenever the token expires and a refresh token is available, try to refresh the access token.
     * Otherwise, redirect to login.
     */
    this.keycloakAuth.onTokenExpired = () => {
      if (this.keycloakAuth.refreshToken) {
        this.updateToken();
      } else {
        this.authState.next(false);
        this.login();
      }
    };
    /**
     * When failing to refresh the token, redirect to login.
     */
    this.keycloakAuth.onAuthRefreshError = () => {
      log.debug('Failed to refresh the access token. Redirecting to login...');
      this.authState.next(false);
      this.login();
    };
  }

  async login(options: LoginOptions = {}): Promise<void> {
    const { success, error } = this.keycloakAuth.login(options);
    return new Promise<void>((resolve, reject) => {
      success(resolve);
      error(reject);
    });
  }

  async logout(): Promise<void> {
    const { success, error } = this.keycloakAuth.logout();
    return new Promise<void>((resolve, reject) => {
      success(resolve);
      error(reject);
    });
  }

  async accountManagement(): Promise<void> {
    const { success, error } = this.keycloakAuth.accountManagement();
    return new Promise<void>((resolve, reject) => {
      success(resolve);
      error(reject);
    });
  }

  updateToken(): Promise<string> {
    const { success, error } = this.keycloakAuth.updateToken(5);
    return new Promise<string>((resolve, reject) => {
      success(() => resolve(this.keycloakAuth.token));
      error(reject);
    });
  }

  get isAuthenticated(): Promise<boolean> {
    const { authenticated } = this.keycloakAuth;
    return authenticated
      ? Promise.resolve(authenticated)
      : this.isSSOAuthenticated();
  }

  get token(): string {
    return this.keycloakAuth.token;
  }

  get tokenParsed(): Keycloak.KeycloakTokenParsed {
    return this.keycloakAuth.tokenParsed;
  }

  get userProfile(): Promise<Keycloak.KeycloakProfile> {
    const { profile } = this.keycloakAuth;
    return profile ? Promise.resolve(profile) : this.loadUserProfile();
  }

  get onAuthStateChanged(): Observable<boolean> {
    return this.authState.pipe(distinctUntilChanged());
  }

  private async isSSOAuthenticated(): Promise<boolean> {
    const { success, error } = this.keycloakAuth.init({ onLoad: 'check-sso' });
    return new Promise<boolean>((resolve, reject) => {
      success(resolve);
      error(reject);
    });
  }

  private async loadUserProfile(): Promise<Keycloak.KeycloakProfile> {
    const { success, error } = this.keycloakAuth.loadUserProfile();
    return new Promise<Keycloak.KeycloakProfile>((resolve, reject) => {
      success(resolve);
      error(reject);
    });
  }
}
