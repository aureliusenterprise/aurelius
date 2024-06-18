import { TestBed, waitForAsync } from '@angular/core/testing';
import { I18nModule } from './i18n.module';

describe('I18nModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [I18nModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(I18nModule).toBeDefined();
  });
});
