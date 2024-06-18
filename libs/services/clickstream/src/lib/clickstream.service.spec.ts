import { TestBed } from '@angular/core/testing';

import { ClickstreamService } from './clickstream.service';

describe('ClickstreamService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: ClickstreamService = TestBed.get(ClickstreamService);
    expect(service).toBeTruthy();
  });
});
