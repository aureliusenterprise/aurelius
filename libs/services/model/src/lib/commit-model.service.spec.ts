import { TestBed } from '@angular/core/testing';

import { CommitModelService } from './commit-model.service';
import { StoreService } from '@models4insight/redux';
import { AuthenticationService } from '@models4insight/authentication';
import { ProjectService } from '@models4insight/services/project';
import { TaskManagerService } from '@models4insight/task-manager';
import { ConflictsService } from './conflicts.service';

describe('CommitModelService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [
                StoreService,
                { provide: AuthenticationService, useValue: {} },
                { provide: ProjectService, useValue: {} },
                { provide: TaskManagerService, useValue: {} },
                { provide: ConflictsService, useValue: {} },
                CommitModelService,
            ],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: CommitModelService = TestBed.inject(CommitModelService);
        expect(service).toBeTruthy();
    });
});
