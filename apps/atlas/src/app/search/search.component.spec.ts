import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { RouterTestingModule } from '@angular/router/testing';
import { of } from 'rxjs';

import { SearchComponent } from './search.component';
import { EntitySearchService } from './services/search/entity-search.service';
import { TranslateService } from '@ngx-translate/core';

describe('SearchComponent', () => {
    let component: SearchComponent;
    let fixture: ComponentFixture<SearchComponent>;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            imports: [RouterTestingModule],
            declarations: [SearchComponent],
            schemas: [NO_ERRORS_SCHEMA],
            providers: [
                { provide: EntitySearchService, useValue: { select: () => of(''), filters: {} } },
                { provide: TranslateService, useValue: { get: () => of('') } },
            ],
            teardown: { destroyAfterEach: false },
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(SearchComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
