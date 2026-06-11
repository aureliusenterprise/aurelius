import { TestBed } from '@angular/core/testing';

import { RetrieveModelService } from './retrieve-model.service';
import { StoreService } from '@models4insight/redux';
import { AuthenticationService } from '@models4insight/authentication';
import { ProjectService } from '@models4insight/services/project';
import { of } from 'rxjs';

describe('RetrieveModelService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [
                StoreService,
                { provide: AuthenticationService, useValue: {} },
                { provide: ProjectService, useValue: { select: (key: string) => of() } },
                RetrieveModelService,
            ],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: RetrieveModelService = TestBed.inject(RetrieveModelService);
        expect(service).toBeTruthy();
    });
});
