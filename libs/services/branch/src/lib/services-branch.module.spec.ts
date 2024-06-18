import { TestBed, waitForAsync } from '@angular/core/testing';
import { ServicesBranchModule } from './services-branch.module';

describe('ServicesBranchModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [ServicesBranchModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(ServicesBranchModule).toBeDefined();
  });
});
