import { TestBed, waitForAsync } from '@angular/core/testing';
import { Modelview2Module } from './modelview2.module';

describe('Modelview2Module', () => {
  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [Modelview2Module],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  it('should create', () => {
    expect(Modelview2Module).toBeDefined();
  });
});
