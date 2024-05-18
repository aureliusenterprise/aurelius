import { TestBed } from '@angular/core/testing';

import { BreadCrumbsService } from './bread-crumbs.service';

describe('BreadCrumbsService', () => {
  let service: BreadCrumbsService;

  beforeEach(() => {
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } });
    service = TestBed.inject(BreadCrumbsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
