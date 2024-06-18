import { TestBed, waitForAsync } from '@angular/core/testing';
import { ElasticApiModule } from './elastic-api.module';

describe('ElasticApiModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [ElasticApiModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(ElasticApiModule).toBeDefined();
  });
});
