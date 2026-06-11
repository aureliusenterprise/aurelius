import { TestBed } from '@angular/core/testing';

import { RecentProjectsService } from './recent-projects.service';
import { StoreService } from '@models4insight/redux';
import { ProjectsService } from '@models4insight/services/project';
import { UserInfoService } from './user-info.service';

describe('RecentProjectsService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [
                StoreService,
                { provide: ProjectsService, useValue: {} },
                { provide: UserInfoService, useValue: {} },
                RecentProjectsService,
            ],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: RecentProjectsService = TestBed.inject(RecentProjectsService);
        expect(service).toBeTruthy();
    });
});
