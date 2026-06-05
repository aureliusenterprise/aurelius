import { TestBed } from '@angular/core/testing';

import { FavoriteProjectsService } from './favorite-projects.service';
import { StoreService } from '@models4insight/redux';
import { ProjectService, ProjectsService } from '@models4insight/services/project';
import { UserInfoService } from './user-info.service';

describe('FavoriteProjectsService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [
                StoreService,
                { provide: ProjectsService, useValue: {} },
                { provide: ProjectService, useValue: {} },
                { provide: UserInfoService, useValue: {} },
                FavoriteProjectsService,
            ],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: FavoriteProjectsService = TestBed.inject(FavoriteProjectsService);
        expect(service).toBeTruthy();
    });
});
