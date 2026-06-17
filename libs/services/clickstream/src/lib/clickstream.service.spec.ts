import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { ClickstreamService } from './clickstream.service';
import { StoreService } from '@models4insight/redux';
import { AuthenticationService } from '@models4insight/authentication';
import { ClickstreamConfig, ClickstreamConfigService } from './clickstream-config.service';
import { of } from 'rxjs';

describe('ClickstreamService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [
                StoreService,
                { provide: AuthenticationService, useValue: { get: () => of(false) } },
                { provide: ClickstreamConfigService, useValue: { enabled: false } },
                { provide: Router, useValue: { events: of() } },
                ClickstreamService,
            ],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: ClickstreamService = TestBed.get(ClickstreamService);
        expect(service).toBeTruthy();
    });
});
