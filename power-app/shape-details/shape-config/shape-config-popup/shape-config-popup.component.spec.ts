import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShapeConfigPopupComponent } from './shape-config-popup.component';

describe('ShapeConfigPopupComponent', () => {
  let component: ShapeConfigPopupComponent;
  let fixture: ComponentFixture<ShapeConfigPopupComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShapeConfigPopupComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShapeConfigPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
