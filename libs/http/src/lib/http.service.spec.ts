import { TestBed, inject } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { HttpClient, HttpInterceptor } from '@angular/common/http';

import { HttpService } from './http.service';
import { HttpCacheService } from './http-cache.service';
import { ErrorHandlerInterceptor } from './error-handler.interceptor';
import { CacheInterceptor } from './cache.interceptor';
import { IECacheHeaderInterceptor } from './ie-cache-header-interceptor';

describe('HttpService', () => {
    let httpCacheService: HttpCacheService;
    let http: HttpClient & HttpService;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [
                ErrorHandlerInterceptor,
                IECacheHeaderInterceptor,
                CacheInterceptor,
                HttpCacheService,
                {
                    provide: HttpClient,
                    useClass: HttpService,
                },
            ],
            teardown: { destroyAfterEach: false },
        });
    });

    beforeEach(inject(
        [HttpClient, HttpTestingController, HttpCacheService],
        (_http: HttpClient & HttpService, _httpMock: HttpTestingController, _httpCacheService: HttpCacheService) => {
            http = _http;
            httpMock = _httpMock;
            httpCacheService = _httpCacheService;
        },
    ));

    afterEach(() => {
        httpCacheService.cleanCache();
        httpMock.verify();
    });

    it('should use error handler and no cache by default', () => {
        // Act
        const request = http.get('/toto');

        // Assert
        request.subscribe(() => {
            const interceptors = (http as any).interceptors;
            expect(interceptors.some((i: HttpInterceptor) => i instanceof ErrorHandlerInterceptor)).toBeTruthy();
            expect(interceptors.some((i: HttpInterceptor) => i instanceof CacheInterceptor)).toBeFalsy();
        });
        httpMock.expectOne({}).flush({});
    });

    it('should use cache', () => {
        // Act: cache() returns a new HttpService instance with CacheInterceptor added
        const cachedHttp = http.cache();
        const request = cachedHttp.get('/toto');

        // Assert
        request.subscribe(() => {
            const interceptors = (cachedHttp as any).interceptors;
            expect(interceptors.some((i: HttpInterceptor) => i instanceof ErrorHandlerInterceptor)).toBeTruthy();
            expect(interceptors.some((i: HttpInterceptor) => i instanceof CacheInterceptor)).toBeTruthy();
        });
        httpMock.expectOne({}).flush({});
    });

    it('should skip error handler', () => {
        // Act: skipErrorHandler() returns a new HttpService instance without ErrorHandlerInterceptor
        const skippedHttp = http.skipErrorHandler();
        const request = skippedHttp.get('/toto');

        // Assert
        request.subscribe(() => {
            const interceptors = (skippedHttp as any).interceptors;
            expect(interceptors.some((i: HttpInterceptor) => i instanceof ErrorHandlerInterceptor)).toBeFalsy();
            expect(interceptors.some((i: HttpInterceptor) => i instanceof CacheInterceptor)).toBeFalsy();
        });
        httpMock.expectOne({}).flush({});
    });
});
