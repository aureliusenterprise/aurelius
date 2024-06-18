import { TestBed, waitForAsync } from '@angular/core/testing';
import { ServicesProjectModule } from './services-project.module';

describe('ServicesProjectModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [ServicesProjectModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(ServicesProjectModule).toBeDefined();
  });
});
