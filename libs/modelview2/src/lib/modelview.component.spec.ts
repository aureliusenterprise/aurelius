import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { AuthenticationService } from '@models4insight/authentication';
import { VersionService } from '@models4insight/version';
import { of } from 'rxjs';

import { ModelviewComponent } from './modelview.component';

describe('ModelviewComponent', () => {
    let component: ModelviewComponent;
    let fixture: ComponentFixture<ModelviewComponent>;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            declarations: [ModelviewComponent],
            schemas: [NO_ERRORS_SCHEMA],
            providers: [
                { provide: ModelService, useValue: { select: () => of() } },
                { provide: ProjectService, useValue: {} },
                { provide: AuthenticationService, useValue: {} },
                { provide: VersionService, useValue: {} },
            ],
            teardown: { destroyAfterEach: false },
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ModelviewComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
