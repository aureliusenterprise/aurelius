import { TestBed, waitForAsync } from '@angular/core/testing';
import { NotificationsModule } from './notifications.module';

describe('NotificationsModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [NotificationsModule.forRoot()],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(NotificationsModule).toBeDefined();
  });
});
