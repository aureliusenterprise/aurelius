import { TestBed } from '@angular/core/testing';

import { RecentProjectsService } from './recent-projects.service';

describe('RecentProjectsService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: RecentProjectsService = TestBed.inject(
      RecentProjectsService
    );
    expect(service).toBeTruthy();
  });
});
