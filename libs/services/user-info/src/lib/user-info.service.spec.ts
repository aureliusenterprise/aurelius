import { TestBed } from '@angular/core/testing';

import { UserInfoService } from './user-info.service';

describe('UserInfoService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({ teardown: { destroyAfterEach: false } })
  );

  it('should be created', () => {
    const service: UserInfoService = TestBed.inject(UserInfoService);
    expect(service).toBeTruthy();
  });
});
