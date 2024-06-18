import { TestBed } from '@angular/core/testing';

import { ConflictsService } from './conflicts.service';

describe('ConflictsService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: ConflictsService = TestBed.get(ConflictsService);
    expect(service).toBeTruthy();
  });
});
