import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { RouterTestingModule } from '@angular/router/testing';
import { of } from 'rxjs';

import { PeopleComponent } from './people.component';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';

describe('PeopleComponent', () => {
    let component: PeopleComponent;
    let fixture: ComponentFixture<PeopleComponent>;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            imports: [RouterTestingModule],
            declarations: [PeopleComponent],
            schemas: [NO_ERRORS_SCHEMA],
            providers: [
                {
                    provide: EntityDetailsService,
                    useValue: {
                        select: (path: any) =>
                            Array.isArray(path) && path.includes('relationshipAttributes')
                                ? of({})
                                : of({ entity: { relationshipAttributes: {} } }),
                    },
                },
            ],
            teardown: { destroyAfterEach: false },
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(PeopleComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
