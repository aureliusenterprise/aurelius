import { TestBed } from '@angular/core/testing';

import { ModelService } from './model.service';
import { StoreService } from '@models4insight/redux';
import { AuthenticationService } from '@models4insight/authentication';
import { ProjectService } from '@models4insight/services/project';
import { of } from 'rxjs';

describe('ModelService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [
                StoreService,
                { provide: AuthenticationService, useValue: {} },
                { provide: ProjectService, useValue: { select: (key: string) => of() } },
                ModelService,
            ],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: ModelService = TestBed.inject(ModelService);
        expect(service).toBeTruthy();
    });
});
