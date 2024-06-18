import { TestBed, waitForAsync } from '@angular/core/testing';
import { ServicesModelModule } from './services-model.module';

describe('ServicesModelModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [ServicesModelModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(ServicesModelModule).toBeDefined();
  });
});
