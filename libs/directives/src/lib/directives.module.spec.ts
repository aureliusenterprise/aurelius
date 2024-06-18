import { TestBed, waitForAsync } from '@angular/core/testing';
import { DirectivesModule } from './directives.module';

describe('DirectivesModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [DirectivesModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(DirectivesModule).toBeDefined();
  });
});
