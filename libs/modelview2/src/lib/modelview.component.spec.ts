import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { ModelviewComponent } from './modelview.component';

describe('ModelviewComponent', () => {
  let component: ModelviewComponent;
  let fixture: ComponentFixture<ModelviewComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [ModelviewComponent],
      teardown: { destroyAfterEach: false },
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ModelviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
