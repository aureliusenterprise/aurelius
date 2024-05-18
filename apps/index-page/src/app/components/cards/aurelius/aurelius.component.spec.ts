import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AureliusComponent } from './aurelius.component';

describe('AureliusComponent', () => {
  let component: AureliusComponent;
  let fixture: ComponentFixture<AureliusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AureliusComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AureliusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
