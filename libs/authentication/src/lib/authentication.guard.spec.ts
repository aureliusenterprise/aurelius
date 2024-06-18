import { TestBed, inject, tick, fakeAsync } from '@angular/core/testing';
import { RouterStateSnapshot, Router } from '@angular/router';

import { AuthenticationService } from './authentication.service';
import { AuthenticationGuard } from './authentication.guard';
import { switchMapTo, tap } from 'rxjs/operators';
import { KeycloakService } from './keycloak.service';

describe('AuthenticationGuard', () => {
  let authenticationGuard: AuthenticationGuard;
  let authenticationService: AuthenticationService;
  let mockSnapshot: RouterStateSnapshot;

  beforeEach(() => {
    mockSnapshot = jasmine.createSpyObj<RouterStateSnapshot>(
      'RouterStateSnapshot',
      ['toString']
    );

    TestBed.configureTestingModule({
      providers: [
        AuthenticationGuard,
        AuthenticationService,
        KeycloakService,
        Router,
      ],
      teardown: { destroyAfterEach: false },
    });
  });

  beforeEach(inject(
    [AuthenticationGuard, AuthenticationService],
    (_authenticationGuard: AuthenticationGuard) => {
      authenticationGuard = _authenticationGuard;
    }
  ));

  it('should have a canActivate method', () => {
    expect(typeof authenticationGuard.canActivate).toBe('function');
  });

  it('should return true if user is authenticated', fakeAsync(() => {
    // Make sure the user is authenticated
    const loginRequest = authenticationService.login().pipe(
      switchMapTo(authenticationService.isAuthenticated()),
      tap((isAuthenticated: boolean) => expect(isAuthenticated).toBeTruthy())
    );

    const canActivate = loginRequest.pipe(
      switchMapTo(authenticationGuard.canActivate(null, mockSnapshot))
    );

    tick();

    canActivate.subscribe((canActivate: boolean) =>
      expect(canActivate).toBeTruthy()
    );
  }));

  it('should return false and redirect to login if user is not authenticated', fakeAsync(() => {
    spyOn(authenticationService, 'login');

    // Make sure the user is not authenticated
    const loginRequest = authenticationService.logout().pipe(
      switchMapTo(authenticationService.isAuthenticated()),
      tap((isAuthenticated: boolean) => expect(isAuthenticated).toBeFalsy())
    );

    const canActivate = loginRequest.pipe(
      switchMapTo(authenticationGuard.canActivate(null, mockSnapshot))
    );

    tick();

    canActivate.subscribe((canActivate: boolean) => {
      expect(canActivate).toBeTruthy();
      expect(authenticationService.login).toHaveBeenCalled();
    });
  }));
});
