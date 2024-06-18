import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

/**
 * Appends no-cache headers to the request.
 * This solves a problem particularly with Internet Explorer where REST API responses would be cached by the browser, showing outdated information in the app.
 */
@Injectable()
export class IECacheHeaderInterceptor implements HttpInterceptor {
  intercept(
    request: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    if (request.method === 'GET') {
      const customRequest = request.clone({
        headers: request.headers
          .set('Cache-Control', 'no-cache')
          .set('Pragma', 'no-cache'),
      });
      return next.handle(customRequest);
    }

    return next.handle(request);
  }
}
