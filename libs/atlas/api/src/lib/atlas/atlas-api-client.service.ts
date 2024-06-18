import { HttpHandler } from '@angular/common/http';
import { Injectable, Injector } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { HttpService } from '@models4insight/http';
import { AuthorizationHeaderInterceptor } from 'libs/http/src/lib/authorization-header.interceptor';

@Injectable()
export class AtlasApiClient extends HttpService {
  constructor(
    httpHandler: HttpHandler,
    injector: Injector,
    authenticationService: AuthenticationService
  ) {
    super(httpHandler, injector, [
      new AuthorizationHeaderInterceptor(authenticationService),
    ]);
  }
}
