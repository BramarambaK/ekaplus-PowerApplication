import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PricingPopupComponent } from './pricing-popup.component';

describe('PricingPopupComponent', () => {
  let component: PricingPopupComponent;
  let fixture: ComponentFixture<PricingPopupComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PricingPopupComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PricingPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
