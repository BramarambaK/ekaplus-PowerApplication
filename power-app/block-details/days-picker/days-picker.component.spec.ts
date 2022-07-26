import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DaysPickerComponent } from './days-picker.component';

describe('DaysPickerComponent', () => {
  let component: DaysPickerComponent;
  let fixture: ComponentFixture<DaysPickerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DaysPickerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DaysPickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
