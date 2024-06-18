import { TestBed } from '@angular/core/testing';

import { CommitModelService } from './commit-model.service';

describe('CommitModelService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: CommitModelService = TestBed.inject(CommitModelService);
    expect(service).toBeTruthy();
  });
});
