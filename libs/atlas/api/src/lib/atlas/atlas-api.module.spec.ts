import { TestBed, waitForAsync } from '@angular/core/testing';
import { AtlasApiModule } from './atlas-api.module';

describe('AtlasApiModule', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [AtlasApiModule],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(AtlasApiModule).toBeDefined();
  });
});
