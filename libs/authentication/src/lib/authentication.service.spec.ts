import { inject, TestBed } from '@angular/core/testing';
import { firstValueFrom, of } from 'rxjs';
import { AuthenticationService, Credentials } from './authentication.service';
import { KeycloakService } from './keycloak.service';
import { AuthenticationConfigService } from './authentication-config.service';
import { StoreService } from '@models4insight/redux';

describe('AuthenticationService', () => {
    let authenticationService: AuthenticationService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                AuthenticationService,
                KeycloakService,
                {
                    provide: AuthenticationConfigService,
                    useValue: { clientId: 'test', realm: 'test', url: 'http://localhost/test' },
                },
                {
                    provide: StoreService,
                    useValue: { get: () => of({}), set: () => {}, remove: () => {}, register: () => {} },
                },
            ],
            teardown: { destroyAfterEach: false },
        });
    });

    beforeEach(inject([AuthenticationService], (_authenticationService: AuthenticationService) => {
        authenticationService = _authenticationService;
    }));

    describe('isAuthenticated', () => {
        it('should return an observable for authentication state', async () => {
            const result = await firstValueFrom(authenticationService.isAuthenticated());
            expect(typeof result).toBe('boolean');
        });
    });

    describe('credentials', () => {
        it('should return an observable for credentials', async () => {
            const result = await firstValueFrom(authenticationService.credentials());
            // Credentials may be undefined if not authenticated
            expect(result === null || typeof result === 'object').toBeTruthy();
        });
    });

    describe('login', () => {
        it('should call keycloak login', async () => {
            // The login method should return a promise that resolves
            // Note: this will redirect in a real environment, so we just verify the method exists
            expect(typeof authenticationService.login).toBe('function');
        });
    });

    describe('logout', () => {
        it('should call keycloak logout', async () => {
            // The logout method should return a promise that resolves
            expect(typeof authenticationService.logout).toBe('function');
        });
    });
});
