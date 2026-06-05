import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { of } from 'rxjs';

import { CreateEntityComponent } from './create-entity.component';
import { EntityDetailsService } from '../services/entity-details/entity-details.service';
import { EntityAPIService } from '@models4insight/atlas/api';

describe('CreateEntityComponent', () => {
    let component: CreateEntityComponent;
    let fixture: ComponentFixture<CreateEntityComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [CreateEntityComponent],
            schemas: [NO_ERRORS_SCHEMA],
            providers: [
                { provide: EntityAPIService, useValue: {} },
                { provide: EntityDetailsService, useValue: { select: () => of({}) } },
            ],
            teardown: { destroyAfterEach: false },
        }).compileComponents();

        fixture = TestBed.createComponent(CreateEntityComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
