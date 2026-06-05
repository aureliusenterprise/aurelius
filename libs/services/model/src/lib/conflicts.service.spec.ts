import { TestBed } from '@angular/core/testing';

import { ConflictsService } from './conflicts.service';
import { StoreService } from '@models4insight/redux';

describe('ConflictsService', () => {
    beforeEach(() =>
        TestBed.configureTestingModule({
            providers: [StoreService, ConflictsService],
            teardown: { destroyAfterEach: false },
        }),
    );

    it('should be created', () => {
        const service: ConflictsService = TestBed.get(ConflictsService);
        expect(service).toBeTruthy();
    });
});
