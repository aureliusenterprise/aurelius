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

  it('should clear breadcrumbs when empty arrays are received', (done) => {
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
      if (emitCount === 1) {
        expect(breadcrumbs.length).toBe(1);
        expect(breadcrumbs[0].guid).toBe('guid1');
        mockDocument$.next(emptyData);
      } else if (emitCount === 2) {
        expect(breadcrumbs.length).toBe(0);
        done();
      }
    });

    mockDocument$.next(initialData);
  });

  it('should clear breadcrumbs and set warning when mismatched arrays are received', (done) => {
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
    service.select('breadcrumbs', { includeFalsy: true }).subscribe(breadcrumbs => {
      emitCount++;
      if (emitCount === 1) {
        expect(breadcrumbs.length).toBe(2);
        mockDocument$.next(mismatchedData);
      } else if (emitCount === 2) {
        expect(breadcrumbs.length).toBe(0);
        service.select('breadcrumbWarning').subscribe(warning => {
          expect(warning).toBe('Breadcrumb path could not be determined');
          done();
        });
      }
    });

    mockDocument$.next(initialData);
  });

  it('should clear breadcrumbs when document has no breadcrumb fields', (done) => {
    const initialData = {
      breadcrumbguid: { raw: ['guid1'] },
      breadcrumbname: { raw: ['Name 1'] },
      breadcrumbtype: { raw: ['Type1'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    const noFieldsData = {} as AppSearchResult<AtlasEntitySearchObject>;

    let emitCount = 0;
    service.select('breadcrumbs').subscribe(breadcrumbs => {
      emitCount++;
      if (emitCount === 1) {
        expect(breadcrumbs.length).toBe(1);
        mockDocument$.next(noFieldsData);
      } else if (emitCount === 2) {
        expect(breadcrumbs.length).toBe(0);
        done();
      }
    });

    mockDocument$.next(initialData);
  });

  it('should preserve breadcrumbs when null document is received', (done) => {
    const initialData = {
      breadcrumbguid: { raw: ['guid1'] },
      breadcrumbname: { raw: ['Name 1'] },
      breadcrumbtype: { raw: ['Type1'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    let emitCount = 0;
    service.select('breadcrumbs').subscribe(breadcrumbs => {
      emitCount++;
      if (emitCount === 1 && breadcrumbs) {
        expect(breadcrumbs.length).toBe(1);
        mockDocument$.next(null);
      } else if (emitCount === 2) {
        fail('Breadcrumbs should not be updated when document is null');
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

  it('should preserve breadcrumbs while document is null during navigation', (done) => {
    const initialData = {
      breadcrumbguid: { raw: ['guid1'] },
      breadcrumbname: { raw: ['Name 1'] },
      breadcrumbtype: { raw: ['Type1'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    const nextData = {
      breadcrumbguid: { raw: ['guid2'] },
      breadcrumbname: { raw: ['Name 2'] },
      breadcrumbtype: { raw: ['Type2'] }
    } as AppSearchResult<AtlasEntitySearchObject>;

    let emitCount = 0;
    service.select('breadcrumbs').subscribe(breadcrumbs => {
      emitCount++;
      if (emitCount === 1) {
        expect(breadcrumbs[0].guid).toBe('guid1');
        // Simulate navigation: document resets to null before new result arrives
        mockDocument$.next(null);
        mockDocument$.next(nextData);
      } else if (emitCount === 2) {
        expect(breadcrumbs[0].guid).toBe('guid2');
        done();
      }
    });

    mockDocument$.next(initialData);
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
