import { TestBed } from '@angular/core/testing';

import { FavoriteProjectsService } from './favorite-projects.service';

describe('FavoriteProjectsService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: FavoriteProjectsService = TestBed.inject(
      FavoriteProjectsService
    );
    expect(service).toBeTruthy();
  });
});
