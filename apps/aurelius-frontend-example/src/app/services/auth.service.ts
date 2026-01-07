import { effect, inject, Injectable, Signal, signal } from "@angular/core";
import { toObservable, toSignal } from "@angular/core/rxjs-interop";
import { KEYCLOAK_EVENT_SIGNAL, KeycloakEventType, ReadyArgs, typeEventArgs } from "keycloak-angular";
import Keycloak, { KeycloakProfile } from "keycloak-js";
import { switchMap } from "rxjs";

@Injectable({
    providedIn: "root",
})
export class AuthService {
    /**
     * A signal that indicates whether the user is authenticated.
     */
    readonly authenticated = signal<boolean>(false);

    /**
     * A signal that returns the Keycloak profile if the user is authenticated.
     */
    readonly profile: Signal<KeycloakProfile | null>;

    /**
     * The Keycloak instance used for authentication.
     */
    private readonly keycloak = inject(Keycloak);

    /**
     * A signal that listens to Keycloak events.
     */
    private readonly keycloakEvents = inject(KEYCLOAK_EVENT_SIGNAL);

    /**
     * Initializes the AuthService and sets up an effect to handle Keycloak events.
     */
    constructor() {
        effect(() => {
            const keycloakEvent = this.keycloakEvents();

            if (keycloakEvent.type === KeycloakEventType.Ready) {
                this.authenticated.set(typeEventArgs<ReadyArgs>(keycloakEvent.args));
            }

            if (keycloakEvent.type === KeycloakEventType.AuthLogout) {
                this.authenticated.set(false);
            }
        });

        const profile$ = toObservable(this.authenticated).pipe(
            switchMap((authenticated) => this.loadUserProfile(authenticated)),
        );

        this.profile = toSignal(profile$, { initialValue: null });
    }

    /**
     * Open the account management page.
     */
    accountManagement(): Promise<void> {
        return this.keycloak.accountManagement();
    }

    /**
     * Log in the user.
     */
    login(): Promise<void> {
        return this.keycloak.login({ redirectUri: window.location.origin });
    }

    /**
     * Log out the user.
     */
    logout(): Promise<void> {
        return this.keycloak.logout({ redirectUri: window.location.origin });
    }

    /**
     * Loads the user profile if the user is authenticated.
     */
    private async loadUserProfile(authenticated: boolean): Promise<KeycloakProfile | null> {
        if (!authenticated) {
            return null;
        }
        return this.keycloak.loadUserProfile();
    }
}
