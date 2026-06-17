import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { of } from 'rxjs';

import { ResultsComponent } from './results.component';
import { AtlasEntitySearchService } from '@models4insight/atlas/api';
import { SearchService } from '../services/search/search.service';

describe('ResultsComponent', () => {
    let component: ResultsComponent;
    let fixture: ComponentFixture<ResultsComponent>;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            declarations: [ResultsComponent],
            schemas: [NO_ERRORS_SCHEMA],
            providers: [
                { provide: AtlasEntitySearchService, useValue: {} },
                { provide: SearchService, useValue: {} },
            ],
            teardown: { destroyAfterEach: false },
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ResultsComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
