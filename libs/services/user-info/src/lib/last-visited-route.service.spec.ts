import { TestBed } from '@angular/core/testing';

import { LastVisitedRouteService } from './last-visited-route.service';

describe('LastVisitedRouteService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: LastVisitedRouteService = TestBed.inject(
      LastVisitedRouteService
    );
    expect(service).toBeTruthy();
  });
});
