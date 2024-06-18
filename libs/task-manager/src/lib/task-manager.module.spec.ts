import { TestBed, waitForAsync } from '@angular/core/testing';
import { TaskManagerModule } from './task-manager.module';

describe('TaskManagerModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [TaskManagerModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(TaskManagerModule).toBeDefined();
  });
});
