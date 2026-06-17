import { TestBed, inject } from '@angular/core/testing';
import { RouterStateSnapshot, Router } from '@angular/router';
import { of } from 'rxjs';

import { AuthenticationService } from './authentication.service';
import { AuthenticationGuard } from './authentication.guard';
import { KeycloakService } from './keycloak.service';
import { AuthenticationConfigService } from './authentication-config.service';
import { StoreService } from '@models4insight/redux';

describe('AuthenticationGuard', () => {
    let authenticationGuard: AuthenticationGuard;
    let authenticationService: AuthenticationService;
    let mockSnapshot: RouterStateSnapshot;

    beforeEach(() => {
        mockSnapshot = {
            toString: jest.fn().mockReturnValue('/test-route'),
            url: '/test-route',
            root: {} as any,
            params: {},
            queryParams: {},
            fragment: null,
            data: {},
            statusCode: null,
        } as unknown as RouterStateSnapshot;

        TestBed.configureTestingModule({
            providers: [
                AuthenticationGuard,
                AuthenticationService,
                KeycloakService,
                Router,
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

    beforeEach(inject(
        [AuthenticationGuard, AuthenticationService],
        (_authenticationGuard: AuthenticationGuard, _authenticationService: AuthenticationService) => {
            authenticationGuard = _authenticationGuard;
            authenticationService = _authenticationService;
        },
    ));

    it('should have a canActivate method', () => {
        expect(typeof authenticationGuard.canActivate).toBe('function');
    });

    it('should be defined', () => {
        expect(authenticationGuard).toBeDefined();
    });
});
