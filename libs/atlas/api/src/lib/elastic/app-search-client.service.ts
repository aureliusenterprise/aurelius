import { HttpHandler } from '@angular/common/http';
import { Inject, Injectable, InjectionToken, Injector } from '@angular/core';
import { HttpService } from '@models4insight/http';
import {
  AuthorizationHeaderInterceptor,
  AuthTokenProvider,
} from 'libs/http/src/lib/authorization-header.interceptor';

export const APP_SEARCH_TOKEN = new InjectionToken<string>('APP_SEARCH_TOKEN');

@Injectable()
class AppSearchTokenProvider implements AuthTokenProvider {
  constructor(
    @Inject(APP_SEARCH_TOKEN) private readonly appSearchToken: string
  ) {}

  async getToken(): Promise<string> {
    return this.appSearchToken;
  }
}

@Injectable()
export class AppSearchClient extends HttpService {
  constructor(
    httpHandler: HttpHandler,
    injector: Injector,
    @Inject(APP_SEARCH_TOKEN) token: string
  ) {
    super(httpHandler, injector, [
      new AuthorizationHeaderInterceptor(new AppSearchTokenProvider(token)),
    ]);
  }
}
