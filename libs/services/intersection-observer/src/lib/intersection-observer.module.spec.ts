import { TestBed, waitForAsync } from '@angular/core/testing';
import { IntersectionObserverModule } from './intersection-observer.module';

describe('IntersectionObserverModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [IntersectionObserverModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(IntersectionObserverModule).toBeDefined();
  });
});
