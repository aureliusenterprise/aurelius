import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Inject, Injectable, InjectionToken } from '@angular/core';
import { from, Observable } from 'rxjs';

export interface AuthTokenProvider {
  getToken: () => Promise<string>;
}

export const AUTH_TOKEN_PROVIDER = new InjectionToken<AuthTokenProvider>(
  'AUTH_TOKEN_PROVIDER'
);

/**
 * Adds an authorization header containing the current Keycloak token to all requests.
 */
@Injectable()
export class AuthorizationHeaderInterceptor<T> implements HttpInterceptor {
  constructor(
    @Inject(AUTH_TOKEN_PROVIDER)
    private readonly authTokenProvider: AuthTokenProvider
  ) {}

  intercept(
    request: HttpRequest<T>,
    next: HttpHandler
  ): Observable<HttpEvent<T>> {
    return from(this.handle(request, next));
  }

  private async handle(
    request: HttpRequest<T>,
    next: HttpHandler
  ): Promise<HttpEvent<T>> {
    const token = await this.authTokenProvider.getToken();

    const clone = request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });

    return next.handle(clone).toPromise();
  }
}
