import { TestBed, waitForAsync } from '@angular/core/testing';
import { ServicesUserInfoModule } from './services-user-info.module';

describe('ServicesUserInfoModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [ServicesUserInfoModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(ServicesUserInfoModule).toBeDefined();
  });
});
