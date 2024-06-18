import { TestBed, waitForAsync } from '@angular/core/testing';
import { GoogleAnalyticsModule } from './google-analytics.module';

describe('GoogleAnalyticsModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [GoogleAnalyticsModule.forRoot()],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(GoogleAnalyticsModule).toBeDefined();
  });
});
