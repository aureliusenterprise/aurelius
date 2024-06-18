import { TestBed } from '@angular/core/testing';

import { IntersectionObserverService } from './intersection-observer.service';

describe('IntersectionObserverService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: IntersectionObserverService = TestBed.get(
      IntersectionObserverService
    );
    expect(service).toBeTruthy();
  });
});
