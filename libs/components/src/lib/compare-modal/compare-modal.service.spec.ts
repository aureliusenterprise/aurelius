import { TestBed } from '@angular/core/testing';

import { CompareModalService } from './compare-modal.service';

describe('CompareModalService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: CompareModalService = TestBed.inject(CompareModalService);
    expect(service).toBeTruthy();
  });
});
