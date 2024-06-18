import { TestBed, waitForAsync } from '@angular/core/testing';
import { ReduxModule } from './redux.module';

describe('ReduxModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [ReduxModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(ReduxModule).toBeDefined();
  });
});
