import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShapeDefinitionComponent } from './shape-definition.component';

describe('ShapeDefinitionComponent', () => {
  let component: ShapeDefinitionComponent;
  let fixture: ComponentFixture<ShapeDefinitionComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShapeDefinitionComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShapeDefinitionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
