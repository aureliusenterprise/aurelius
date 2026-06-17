import { Inject, Injectable } from '@angular/core';
import { Logger } from '@models4insight/logger';
import Keycloak, { KeycloakProfile, KeycloakTokenParsed } from 'keycloak-js';
import { Observable, ReplaySubject, Subject } from 'rxjs';
import { distinctUntilChanged } from 'rxjs/operators';
import { AuthenticationConfig, AuthenticationConfigService } from './authentication-config.service';
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
    private readonly keycloakAuth: Keycloak;
    private readonly authState: Subject<boolean> = new ReplaySubject<boolean>();

    constructor(@Inject(AuthenticationConfigService) config: AuthenticationConfig) {
        this.keycloakAuth = new Keycloak(config);

        this.authState.subscribe((auth: boolean) => log.debug(`Auth state updated: ${auth}`));

        this.keycloakAuth.onReady = (auth) => this.authState.next(auth ?? false);
        this.keycloakAuth.onAuthSuccess = () => this.authState.next(true);
        this.keycloakAuth.onAuthLogout = () => this.authState.next(false);

        this.keycloakAuth.onTokenExpired = () => {
            if (this.keycloakAuth.refreshToken) {
                this.updateToken();
            } else {
                this.authState.next(false);
                this.login();
            }
        };

        this.keycloakAuth.onAuthRefreshError = () => {
            log.debug('Failed to refresh the access token. Redirecting to login...');
            this.authState.next(false);
            this.login();
        };
    }

    login(options: LoginOptions = {}): Promise<void> {
        return this.keycloakAuth.login(options);
    }

    logout(): Promise<void> {
        // keycloak-js v22 maps redirectUri → post_logout_redirect_uri and adds id_token_hint automatically.
        // Derive app root from current path: /<namespace>/atlas/...
        const namespace = window.location.pathname.split('/').filter(Boolean)[0];
        const redirectUri = `${window.location.origin}/${namespace}/atlas/`;
        return this.keycloakAuth.logout({ redirectUri });
    }

    accountManagement(): Promise<void> {
        return this.keycloakAuth.accountManagement();
    }

    updateToken(): Promise<string> {
        return this.keycloakAuth.updateToken(5).then(() => this.keycloakAuth.token ?? '');
    }

    get isAuthenticated(): Promise<boolean> {
        const { authenticated } = this.keycloakAuth;
        return authenticated ? Promise.resolve(true) : this.isSSOAuthenticated();
    }

    get token(): string {
        return this.keycloakAuth.token ?? '';
    }

    get tokenParsed(): KeycloakTokenParsed {
        return this.keycloakAuth.tokenParsed!;
    }

    get userProfile(): Promise<KeycloakProfile> {
        const { profile } = this.keycloakAuth;
        return profile ? Promise.resolve(profile) : this.keycloakAuth.loadUserProfile();
    }

    get onAuthStateChanged(): Observable<boolean> {
        return this.authState.pipe(distinctUntilChanged());
    }

    private isSSOAuthenticated(): Promise<boolean> {
        return this.keycloakAuth.init({ onLoad: 'check-sso' });
    }
}
