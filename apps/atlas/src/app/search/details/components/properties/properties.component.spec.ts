import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { of } from 'rxjs';

import { PropertiesComponent } from './properties.component';
import { PropertiesService } from './properties.service';
import { FilteredPropertiesService } from '../../../services/filtered-properties/filtered-properties.service';

describe('PropertiesComponent', () => {
    let component: PropertiesComponent;
    let fixture: ComponentFixture<PropertiesComponent>;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            declarations: [PropertiesComponent],
            schemas: [NO_ERRORS_SCHEMA],
            providers: [
                { provide: FilteredPropertiesService, useValue: { select: () => of({}), state: of({}) } },
                { provide: PropertiesService, useValue: { select: () => of([]) } },
            ],
            teardown: { destroyAfterEach: false },
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(PropertiesComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
