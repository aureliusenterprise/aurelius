import { Injectable } from '@angular/core';
import { Logger } from '@models4insight/logger';
import { BasicStore, StoreService } from '@models4insight/redux';
import { Observable, of } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { AuthenticationModule } from './authentication.module';
import { KeycloakService } from './keycloak.service';

const log = new Logger('AuthenticationService');

/** Represents the Credentials data object as supplied by Keycloak */
export interface Credentials {
  /** The username of the user */
  username?: string;
  /** The email address of the user */
  email?: string;
  /** The first name of the user */
  firstName?: string;
  /** The last name of the user */
  lastName?: string;
  /** Whether or not the email address of the user has been verified */
  emailVerified?: boolean;
  /** Additional attributes to the user */
  attributes?: {};
}

/** Data object that represents the state of the authentication service */
export interface AuthenticationStoreContext {
  /** The credentials of the current user */
  readonly credentials?: Credentials;
  /** Whether or not the user is currently authenticated */
  readonly isAuthenticated?: boolean;
}

/**
 * Provides a base for authentication workflow.
 */
@Injectable({
  providedIn: AuthenticationModule,
})
export class AuthenticationService extends BasicStore<AuthenticationStoreContext> {
  constructor(
    private keycloakService: KeycloakService,
    storeService: StoreService
  ) {
    super({ name: 'AuthenticationService', storeService });
    this.init();
  }

  private init() {
    // On init, check whether the user is already authenticated. This causes the user to be redirected to the login screen if they are not logged in.
    // If the user is authenticated, update the auth state.
    this.keycloakService.isAuthenticated.then((isAuthenticated) =>
      this.update({
        description: 'Initial auth state updated',
        payload: {
          isAuthenticated: isAuthenticated,
        },
      })
    );

    // Whenever the Keycloak onAuthStateChanged event triggers, update the auth state.
    this.keycloakService.onAuthStateChanged.subscribe((isAuthenticated) =>
      this.update({
        description: 'Auth state updated',
        payload: {
          isAuthenticated: isAuthenticated,
        },
      })
    );

    // Whenever the auth state changes, update the user credentials.
    // If the user is not authenticated, the credentials object should be empty.
    this.isAuthenticated()
      .pipe(
        switchMap((isAuthenticated) =>
          isAuthenticated
            ? this.keycloakService.userProfile
            : of(null as Credentials)
        )
      )
      .subscribe((credentials) =>
        this.update({
          description: 'User credentials updated',
          payload: {
            credentials: credentials,
          },
        })
      );
  }

  /**
   * Authenticates the user.
   */
  login() {
    return this.keycloakService.login();
  }

  /**
   * Logs out the user and clear credentials.
   */
  logout() {
    return this.keycloakService.logout();
  }

  /**
   * Whether the user is authenticated.
   * @return True if the user is authenticated.
   */
  isAuthenticated(): Observable<boolean> {
    return this.select('isAuthenticated');
  }

  /**
   * Redirects the user to their account management panel
   */
  accountManagement() {
    return this.keycloakService.accountManagement();
  }

  /**
   * Gets the current user's credentials.
   * @return The current user's credentials, or null if not authenticated.
   */
  credentials(): Observable<Credentials> {
    return this.select('credentials');
  }

  /**
   * Emits whenever the authentication state changes
   * @return An observable stream of the current authentication state
   */
  onAuthStateChanged(): Observable<boolean> {
    return this.select('isAuthenticated');
  }

  /**
   * Equivalent to `updateToken`.
   */
  async getToken() {
    return this.updateToken();
  }

  /**
   * Attempts to update the token. If not successful, redirects to login.
   * Returns the token, or nothing if no token is available.
   * Does nothing if the user is not logged in.
   */
  async updateToken() {
    const isAuthenticated = await this.get('isAuthenticated', {
      includeFalsy: true,
    });

    let token = null;

    if (!isAuthenticated) return token;

    try {
      token = await this.keycloakService.updateToken();
    } catch {
      this.login();
    }

    return token;
  }
}
