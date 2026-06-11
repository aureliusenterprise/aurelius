import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { PropertiesService } from './properties.service';
import { FilteredPropertiesService } from '../../../services/filtered-properties/filtered-properties.service';

describe('PropertiesService', () => {
    let service: PropertiesService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: FilteredPropertiesService, useValue: { select: () => of({}), state: of({}) } },
                PropertiesService,
            ],
            teardown: { destroyAfterEach: false },
        });
        service = TestBed.inject(PropertiesService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
