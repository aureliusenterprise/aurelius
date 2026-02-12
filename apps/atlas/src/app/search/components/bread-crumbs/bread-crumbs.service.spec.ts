import { TestBed } from '@angular/core/testing';
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
            document$: mockDocument$
          }
        }
      ],
      teardown: { destroyAfterEach: false }
    });
    service = TestBed.inject(BreadCrumbsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should update breadcrumbs when valid data is provided', (done) => {
    const mockSearchResult = {
      breadcrumbguid: { raw: ['guid1', 'guid2'] },
      breadcrumbname: { raw: ['Name 1', 'Name 2'] },
      breadcrumbtype: { raw: ['Type1', 'Type2'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    service.select('breadcrumbs').subscribe(breadcrumbs => {
      if (breadcrumbs) {
        expect(breadcrumbs.length).toBe(2);
        expect(breadcrumbs[0].guid).toBe('guid1');
        expect(breadcrumbs[0].name).toBe('Name 1');
        expect(breadcrumbs[0].typeName).toBe('Type1');
        expect(breadcrumbs[1].guid).toBe('guid2');
        done();
      }
    });

    mockDocument$.next(mockSearchResult);
  });

  it('should preserve breadcrumbs when empty arrays are received', (done) => {
    const initialData = {
      breadcrumbguid: { raw: ['guid1'] },
      breadcrumbname: { raw: ['Name 1'] },
      breadcrumbtype: { raw: ['Type1'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    const emptyData = {
      breadcrumbguid: { raw: [] },
      breadcrumbname: { raw: [] },
      breadcrumbtype: { raw: [] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    let emitCount = 0;
    service.select('breadcrumbs').subscribe(breadcrumbs => {
      emitCount++;
      if (emitCount === 1 && breadcrumbs) {
        // First emit: breadcrumbs should be set
        expect(breadcrumbs.length).toBe(1);
        expect(breadcrumbs[0].guid).toBe('guid1');
        mockDocument$.next(emptyData);
      } else if (emitCount === 2) {
        // Second emit should not happen because breadcrumbs are preserved
        fail('Breadcrumbs should not be updated when empty data is received');
      }
    });

    mockDocument$.next(initialData);

    // Wait and verify breadcrumbs were preserved
    setTimeout(() => {
      service.select('breadcrumbs').subscribe(breadcrumbs => {
        expect(breadcrumbs.length).toBe(1);
        expect(breadcrumbs[0].guid).toBe('guid1');
        done();
      });
    }, 100);
  });

  it('should preserve breadcrumbs when mismatched arrays are received', (done) => {
    const initialData = {
      breadcrumbguid: { raw: ['guid1', 'guid2'] },
      breadcrumbname: { raw: ['Name 1', 'Name 2'] },
      breadcrumbtype: { raw: ['Type1', 'Type2'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    const mismatchedData = {
      breadcrumbguid: { raw: ['guid3'] },
      breadcrumbname: { raw: ['Name 3', 'Name 4'] },
      breadcrumbtype: { raw: ['Type3'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    let emitCount = 0;
    service.select('breadcrumbs').subscribe(breadcrumbs => {
      emitCount++;
      if (emitCount === 1 && breadcrumbs) {
        // First emit: breadcrumbs should be set
        expect(breadcrumbs.length).toBe(2);
        mockDocument$.next(mismatchedData);
      } else if (emitCount === 2) {
        // Should not happen
        fail('Breadcrumbs should not be updated when mismatched data is received');
      }
    });

    mockDocument$.next(initialData);

    // Wait and verify breadcrumbs were preserved
    setTimeout(() => {
      service.select('breadcrumbs').subscribe(breadcrumbs => {
        expect(breadcrumbs.length).toBe(2);
        expect(breadcrumbs[0].guid).toBe('guid1');
        done();
      });
    }, 100);
  });

  it('should preserve breadcrumbs when undefined fields are received', (done) => {
    const initialData = {
      breadcrumbguid: { raw: ['guid1'] },
      breadcrumbname: { raw: ['Name 1'] },
      breadcrumbtype: { raw: ['Type1'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    const undefinedData = {} as AppSearchResult<AtlasEntitySearchObject>;

    let emitCount = 0;
    service.select('breadcrumbs').subscribe(breadcrumbs => {
      emitCount++;
      if (emitCount === 1 && breadcrumbs) {
        expect(breadcrumbs.length).toBe(1);
        mockDocument$.next(undefinedData);
      } else if (emitCount === 2) {
        fail('Breadcrumbs should not be updated when undefined fields are received');
      }
    });

    mockDocument$.next(initialData);

    setTimeout(() => {
      service.select('breadcrumbs').subscribe(breadcrumbs => {
        expect(breadcrumbs.length).toBe(1);
        expect(breadcrumbs[0].guid).toBe('guid1');
        done();
      });
    }, 100);
  });

  it('should update breadcrumbs when new valid data replaces old data', (done) => {
    const initialData = {
      breadcrumbguid: { raw: ['guid1'] },
      breadcrumbname: { raw: ['Name 1'] },
      breadcrumbtype: { raw: ['Type1'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    const newData = {
      breadcrumbguid: { raw: ['guid2', 'guid3'] },
      breadcrumbname: { raw: ['Name 2', 'Name 3'] },
      breadcrumbtype: { raw: ['Type2', 'Type3'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    let emitCount = 0;
    service.select('breadcrumbs').subscribe(breadcrumbs => {
      if (breadcrumbs) {
        emitCount++;
        if (emitCount === 1) {
          expect(breadcrumbs.length).toBe(1);
          expect(breadcrumbs[0].guid).toBe('guid1');
          mockDocument$.next(newData);
        } else if (emitCount === 2) {
          expect(breadcrumbs.length).toBe(2);
          expect(breadcrumbs[0].guid).toBe('guid2');
          expect(breadcrumbs[1].guid).toBe('guid3');
          done();
        }
      }
    });

    mockDocument$.next(initialData);
  });
});
