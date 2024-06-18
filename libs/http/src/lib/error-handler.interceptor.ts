import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Inject, Injectable, Optional } from '@angular/core';
import { Logger } from '@models4insight/logger';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { HttpConfig, HttpConfigService } from './http-config.service';

const log = new Logger('ErrorHandlerInterceptor');

/**
 * Adds a default error handler to all requests.
 */
@Injectable()
export class ErrorHandlerInterceptor implements HttpInterceptor {
  constructor(
    @Optional() @Inject(HttpConfigService) private config: HttpConfig = {}
  ) {}
  intercept(
    request: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    return next
      .handle(request)
      .pipe(catchError((error) => this.errorHandler(error)));
  }

  // Customize the default error handler here if needed
  private errorHandler(response: HttpEvent<any>): Observable<HttpEvent<any>> {
    if (!this.config.production) {
      // Do something with the error
      log.error(response);
    }
    throw response;
  }
}
