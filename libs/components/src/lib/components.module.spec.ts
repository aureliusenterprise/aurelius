import { TestBed, waitForAsync } from '@angular/core/testing';
import { ComponentsModule } from './components.module';

describe('ComponentsModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [ComponentsModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(ComponentsModule).toBeDefined();
  });
});
