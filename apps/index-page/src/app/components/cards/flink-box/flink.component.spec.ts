import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FlinkComponent } from './flink.component';

describe('FlinkComponent', () => {
  let component: FlinkComponent;
  let fixture: ComponentFixture<FlinkComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FlinkComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FlinkComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
