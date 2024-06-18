import { fakeAsync, inject, TestBed, tick } from '@angular/core/testing';
import { switchMapTo, tap } from 'rxjs/operators';
import { AuthenticationService, Credentials } from './authentication.service';
import { KeycloakService } from './keycloak.service';

describe('AuthenticationService', () => {
  let authenticationService: AuthenticationService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [AuthenticationService, KeycloakService],
      teardown: { destroyAfterEach: false },
    });
  });

  beforeEach(inject(
    [AuthenticationService],
    (_authenticationService: AuthenticationService) => {
      authenticationService = _authenticationService;
    }
  ));

  describe('login', () => {
    it('should authenticate user', fakeAsync(() => {
      // Make sure the user is not authenticated
      const isAuthenticated = authenticationService
        .isAuthenticated()
        .pipe(
          tap((isAuthenticated: boolean) => expect(isAuthenticated).toBeFalsy())
        );

      const loginRequest = isAuthenticated.pipe(
        switchMapTo(authenticationService.login()),
        switchMapTo(authenticationService.isAuthenticated())
      );

      tick();

      loginRequest.subscribe((isAuthenticated: boolean) =>
        expect(isAuthenticated).toBeTruthy()
      );
    }));

    it('should return credentials', fakeAsync(() => {
      const loginRequest = authenticationService.login();

      const credentialsRequest = loginRequest.pipe(
        switchMapTo(authenticationService.credentials())
      );

      tick();

      credentialsRequest.subscribe((credentials) => {
        expect(credentials).toBeDefined();
        expect(credentials.username).toBeDefined();
        expect(credentials.email).toBeDefined();
      });
    }));
  });

  describe('logout', () => {
    it('should clear user authentication', fakeAsync(() => {
      // Make sure the user is authenticated.
      const loginRequest = authenticationService.login().pipe(
        switchMapTo(authenticationService.isAuthenticated()),
        tap((isAuthenticated: boolean) => expect(isAuthenticated).toBeTruthy())
      );

      const logoutRequest = loginRequest.pipe(
        switchMapTo(authenticationService.logout()),
        switchMapTo(authenticationService.isAuthenticated()),
        tap((isAuthenticated: boolean) => expect(isAuthenticated).toBeFalsy())
      );

      const credentialsRequest = logoutRequest.pipe(
        switchMapTo(authenticationService.credentials())
      );

      tick();

      credentialsRequest.subscribe((credentials: Credentials) =>
        expect(credentials).toBeNull()
      );
    }));
  });
});
