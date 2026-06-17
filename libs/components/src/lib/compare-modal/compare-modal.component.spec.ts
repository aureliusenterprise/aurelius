import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';

import { CompareModalComponent } from './compare-modal.component';
import { ProjectService } from '@models4insight/services/project';
import { of } from 'rxjs';

describe('CompareModalComponent', () => {
    let component: CompareModalComponent;
    let fixture: ComponentFixture<CompareModalComponent>;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            declarations: [CompareModalComponent],
            providers: [{ provide: ProjectService, useValue: {} }],
            schemas: [NO_ERRORS_SCHEMA],
            teardown: { destroyAfterEach: false },
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(CompareModalComponent);
        component = fixture.componentInstance;

        // Mock the modal ViewChild (normally provided by template elements)
        (component as any).modal = {
            confirmed: of(),
            cancelled: of(),
        };

        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
