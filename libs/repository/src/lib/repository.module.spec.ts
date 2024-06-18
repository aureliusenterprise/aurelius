import { TestBed, waitForAsync } from '@angular/core/testing';
import { RepositoryModule } from './repository.module';

describe('RepositoryModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [RepositoryModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(RepositoryModule).toBeDefined();
  });
});
