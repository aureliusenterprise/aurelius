import { TestBed } from '@angular/core/testing';

import { RetrieveModelService } from './retrieve-model.service';

describe('RetrieveModelService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: RetrieveModelService = TestBed.inject(RetrieveModelService);
    expect(service).toBeTruthy();
  });
});
