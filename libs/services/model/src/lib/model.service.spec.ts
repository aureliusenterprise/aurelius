import { TestBed } from '@angular/core/testing';

import { ModelService } from './model.service';

describe('ModelServiceService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: ModelService = TestBed.inject(ModelService);
    expect(service).toBeTruthy();
  });
});
