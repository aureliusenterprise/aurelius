import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { PeopleComponent } from './people.component';

describe('PeopleComponent', () => {
  let component: PeopleComponent;
  let fixture: ComponentFixture<PeopleComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
    declarations: [PeopleComponent],
    teardown: { destroyAfterEach: false }
})
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PeopleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });


describe('deduplicate()', () => {
  it('should return empty array if input is null or undefined', () => {
    expect(component.deduplicate(null as any)).toEqual([]);
    expect(component.deduplicate(undefined as any)).toEqual([]);
  });

  it('should return empty array if input is empty', () => {
    expect(component.deduplicate([])).toEqual([]);
  });

  it('should remove duplicates based on guid, preserving first occurrence', () => {
    const items = [
      { guid: '1', displayText: 'Alice' },
      { guid: '2', displayText: 'Bob'   },
      { guid: '1', displayText: 'Alice Duplicate' },
      { guid: '3', displayText: 'Charlie' },
    ];
    const result = component.deduplicate(items);
    expect(result.length).toBe(3);
    expect(result).toEqual([
      { guid: '1', displayText: 'Alice' },
      { guid: '2', displayText: 'Bob'   },
      { guid: '3', displayText: 'Charlie' },
    ]);
  });
})
});
