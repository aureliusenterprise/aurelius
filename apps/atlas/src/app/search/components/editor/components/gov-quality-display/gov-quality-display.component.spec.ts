import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GovQualityDisplayComponent } from './gov-quality-display.component';

describe('GovQualityDisplayComponent', () => {
  let component: GovQualityDisplayComponent;
  let fixture: ComponentFixture<GovQualityDisplayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [GovQualityDisplayComponent],
      teardown: { destroyAfterEach: false },
    }).compileComponents();

    fixture = TestBed.createComponent(GovQualityDisplayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
