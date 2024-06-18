import { TestBed, waitForAsync } from '@angular/core/testing';
import { ClickstreamModule } from './clickstream.module';

describe('ClickstreamModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [ClickstreamModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(ClickstreamModule).toBeDefined();
  });
});
