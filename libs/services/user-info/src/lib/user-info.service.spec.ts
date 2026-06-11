import { TestBed } from '@angular/core/testing';

import { UserInfoService } from './user-info.service';
import { StoreService } from '@models4insight/redux';
import { AuthenticationService } from '@models4insight/authentication';
import { of } from 'rxjs';

describe('UserInfoService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [
                StoreService,
                { provide: AuthenticationService, useValue: { isAuthenticated: () => of(false) } },
                UserInfoService,
            ],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: UserInfoService = TestBed.inject(UserInfoService);
        expect(service).toBeTruthy();
    });
});
