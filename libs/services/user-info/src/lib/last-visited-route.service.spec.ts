import { TestBed } from '@angular/core/testing';

import { LastVisitedRouteService } from './last-visited-route.service';
import { UserInfoService } from './user-info.service';
import { of } from 'rxjs';

describe('LastVisitedRouteService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [
                { provide: UserInfoService, useValue: { get: () => of(), select: () => of(), update: () => {} } },
                LastVisitedRouteService,
            ],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: LastVisitedRouteService = TestBed.inject(LastVisitedRouteService);
        expect(service).toBeTruthy();
    });
});
