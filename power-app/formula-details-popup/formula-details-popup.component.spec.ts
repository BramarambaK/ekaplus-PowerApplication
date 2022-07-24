import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FormulaDetailsPopupComponent } from './formula-details-popup.component';

describe('FormulaDetailsPopupComponent', () => {
  let component: FormulaDetailsPopupComponent;
  let fixture: ComponentFixture<FormulaDetailsPopupComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FormulaDetailsPopupComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FormulaDetailsPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
