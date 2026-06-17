import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';
import { AppSearchResult, AtlasEntitySearchObject } from '@models4insight/atlas/api';
import { BreadCrumbsService } from './bread-crumbs.service';
import { $APP_SEARCH_DOCUMENT_PROVIDER } from '../../services/element-search/app-search-document-provider';

describe('BreadCrumbsService', () => {
    let service: BreadCrumbsService;
    let mockDocument$: BehaviorSubject<AppSearchResult<AtlasEntitySearchObject>>;

    beforeEach(() => {
        mockDocument$ = new BehaviorSubject<AppSearchResult<AtlasEntitySearchObject>>(null);

        TestBed.configureTestingModule({
            providers: [
                BreadCrumbsService,
                {
                    provide: $APP_SEARCH_DOCUMENT_PROVIDER,
                    useValue: {
                        document$: mockDocument$,
                    },
                },
            ],
            teardown: { destroyAfterEach: false },
        });
        service = TestBed.inject(BreadCrumbsService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    it('should update breadcrumbs when valid data is provided', fakeAsync(() => {
        const mockSearchResult = {
            breadcrumbguid: { raw: ['guid1', 'guid2'] },
            breadcrumbname: { raw: ['Name 1', 'Name 2'] },
            breadcrumbtype: { raw: ['Type1', 'Type2'] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const breadcrumbs: any[] = [];
        service.select('breadcrumbs').subscribe((b) => breadcrumbs.push(b));

        mockDocument$.next(mockSearchResult);
        tick();

        // Filter out empty/falsy initial emissions - we care about the data emission
        const validBreadcrumbs = breadcrumbs.filter((b) => b && b.length > 0);
        expect(validBreadcrumbs.length).toBe(1);
        expect(validBreadcrumbs[0].length).toBe(2);
        expect(validBreadcrumbs[0][0].guid).toBe('guid1');
        expect(validBreadcrumbs[0][0].name).toBe('Name 1');
        expect(validBreadcrumbs[0][0].typeName).toBe('Type1');
        expect(validBreadcrumbs[0][1].guid).toBe('guid2');
    }));

    it('should clear breadcrumbs when empty arrays are received', fakeAsync(() => {
        const initialData = {
            breadcrumbguid: { raw: ['guid1'] },
            breadcrumbname: { raw: ['Name 1'] },
            breadcrumbtype: { raw: ['Type1'] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const emptyData = {
            breadcrumbguid: { raw: [] },
            breadcrumbname: { raw: [] },
            breadcrumbtype: { raw: [] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const breadcrumbs: any[] = [];
        service.select('breadcrumbs', { includeFalsy: true }).subscribe((b) => breadcrumbs.push(b));

        mockDocument$.next(initialData);
        tick();

        // Check last emission has the initial data
        const afterInitial = breadcrumbs[breadcrumbs.length - 1];
        expect(afterInitial.length).toBe(1);
        expect(afterInitial[0].guid).toBe('guid1');

        mockDocument$.next(emptyData);
        tick();

        // Check last emission is empty array
        const afterEmpty = breadcrumbs[breadcrumbs.length - 1];
        expect(afterEmpty.length).toBe(0);
    }));

    it('should clear breadcrumbs and set warning when mismatched arrays are received', fakeAsync(() => {
        const initialData = {
            breadcrumbguid: { raw: ['guid1', 'guid2'] },
            breadcrumbname: { raw: ['Name 1', 'Name 2'] },
            breadcrumbtype: { raw: ['Type1', 'Type2'] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const mismatchedData = {
            breadcrumbguid: { raw: ['guid3'] },
            breadcrumbname: { raw: ['Name 3', 'Name 4'] },
            breadcrumbtype: { raw: ['Type3'] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const breadcrumbs: any[] = [];
        service.select('breadcrumbs', { includeFalsy: true }).subscribe((b) => breadcrumbs.push(b));

        mockDocument$.next(initialData);
        tick();

        // Check last emission has initial data with 2 items
        expect(breadcrumbs[breadcrumbs.length - 1].length).toBe(2);

        mockDocument$.next(mismatchedData);
        tick();

        // Check last emission is empty array (cleared due to mismatch)
        expect(breadcrumbs[breadcrumbs.length - 1].length).toBe(0);

        const warnings: string[] = [];
        service.select('breadcrumbWarning').subscribe((w) => warnings.push(w));
        tick();

        expect(warnings.some((w) => w === 'Breadcrumb path could not be determined')).toBe(true);
    }));

    it('should clear breadcrumbs when document has no breadcrumb fields', fakeAsync(() => {
        const initialData = {
            breadcrumbguid: { raw: ['guid1'] },
            breadcrumbname: { raw: ['Name 1'] },
            breadcrumbtype: { raw: ['Type1'] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const noFieldsData = {} as AppSearchResult<AtlasEntitySearchObject>;

        const breadcrumbs: any[] = [];
        service.select('breadcrumbs', { includeFalsy: true }).subscribe((b) => breadcrumbs.push(b));

        mockDocument$.next(initialData);
        tick();

        expect(breadcrumbs[breadcrumbs.length - 1].length).toBe(1);

        mockDocument$.next(noFieldsData);
        tick();

        expect(breadcrumbs[breadcrumbs.length - 1].length).toBe(0);
    }));

    it('should clear breadcrumbs when null document is received', fakeAsync(() => {
        const initialData = {
            breadcrumbguid: { raw: ['guid1'] },
            breadcrumbname: { raw: ['Name 1'] },
            breadcrumbtype: { raw: ['Type1'] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const breadcrumbs: any[] = [];
        service.select('breadcrumbs', { includeFalsy: true }).subscribe((b) => breadcrumbs.push(b));

        mockDocument$.next(initialData);
        tick();

        expect(breadcrumbs[breadcrumbs.length - 1].length).toBe(1);

        mockDocument$.next(null);
        tick();

        expect(breadcrumbs[breadcrumbs.length - 1].length).toBe(0);
    }));

    it('should clear then update breadcrumbs during navigation to a new entity', fakeAsync(() => {
        const initialData = {
            breadcrumbguid: { raw: ['guid1'] },
            breadcrumbname: { raw: ['Name 1'] },
            breadcrumbtype: { raw: ['Type1'] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const nextData = {
            breadcrumbguid: { raw: ['guid2'] },
            breadcrumbname: { raw: ['Name 2'] },
            breadcrumbtype: { raw: ['Type2'] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const breadcrumbs: any[] = [];
        service.select('breadcrumbs', { includeFalsy: true }).subscribe((b) => breadcrumbs.push(b));

        mockDocument$.next(initialData);
        tick();

        expect(breadcrumbs[breadcrumbs.length - 1][0].guid).toBe('guid1');

        mockDocument$.next(null);
        tick();

        expect(breadcrumbs[breadcrumbs.length - 1].length).toBe(0);

        mockDocument$.next(nextData);
        tick();

        expect(breadcrumbs[breadcrumbs.length - 1][0].guid).toBe('guid2');
    }));

    it('should update breadcrumbs when new valid data replaces old data', fakeAsync(() => {
        const initialData = {
            breadcrumbguid: { raw: ['guid1'] },
            breadcrumbname: { raw: ['Name 1'] },
            breadcrumbtype: { raw: ['Type1'] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const newData = {
            breadcrumbguid: { raw: ['guid2', 'guid3'] },
            breadcrumbname: { raw: ['Name 2', 'Name 3'] },
            breadcrumbtype: { raw: ['Type2', 'Type3'] },
        } as AppSearchResult<AtlasEntitySearchObject>;

        const breadcrumbs: any[] = [];
        service.select('breadcrumbs').subscribe((b) => breadcrumbs.push(b));

        mockDocument$.next(initialData);
        tick();

        // Check last emission has initial data
        expect(breadcrumbs[breadcrumbs.length - 1].length).toBe(1);
        expect(breadcrumbs[breadcrumbs.length - 1][0].guid).toBe('guid1');

        mockDocument$.next(newData);
        tick();

        // Check last emission has new data
        expect(breadcrumbs[breadcrumbs.length - 1].length).toBe(2);
        expect(breadcrumbs[breadcrumbs.length - 1][0].guid).toBe('guid2');
        expect(breadcrumbs[breadcrumbs.length - 1][1].guid).toBe('guid3');
    }));
});
