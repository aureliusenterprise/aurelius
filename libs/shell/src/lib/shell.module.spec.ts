import { TestBed, waitForAsync } from '@angular/core/testing';
import { ShellModule } from './shell.module';

describe('ShellModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [ShellModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(ShellModule).toBeDefined();
  });
});
