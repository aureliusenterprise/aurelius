import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { of } from 'rxjs';

import { BreadCrumbsComponent } from './bread-crumbs.component';
import { SearchResultService } from '../../services/search-result/search-result.service';
import { $APP_SEARCH_DOCUMENT_PROVIDER } from '../../services/element-search/app-search-document-provider';

describe('BreadCrumbsComponent', () => {
    let component: BreadCrumbsComponent;
    let fixture: ComponentFixture<BreadCrumbsComponent>;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            declarations: [BreadCrumbsComponent],
            schemas: [NO_ERRORS_SCHEMA],
            providers: [
                { provide: SearchResultService, useValue: { document$: of({}) } },
                { provide: $APP_SEARCH_DOCUMENT_PROVIDER, useValue: { document$: of({}) } },
            ],
            teardown: { destroyAfterEach: false },
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(BreadCrumbsComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
