import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShapeDefinitionEditComponent } from './shape-config-cell-edit.component';

describe('ShapeDefinitionEditComponent', () => {
  let component: ShapeDefinitionEditComponent;
  let fixture: ComponentFixture<ShapeDefinitionEditComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShapeDefinitionEditComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShapeDefinitionEditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
