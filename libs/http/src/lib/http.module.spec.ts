import { TestBed, waitForAsync } from '@angular/core/testing';
import { HttpModule } from './http.module';

describe('HttpModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [HttpModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(HttpModule).toBeDefined();
  });
});
