import { TestBed } from '@angular/core/testing';

import { CompareModalService } from './compare-modal.service';
import { ProjectService } from '@models4insight/services/project';

describe('CompareModalService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [{ provide: ProjectService, useValue: {} }, CompareModalService],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: CompareModalService = TestBed.inject(CompareModalService);
        expect(service).toBeTruthy();
    });
});
