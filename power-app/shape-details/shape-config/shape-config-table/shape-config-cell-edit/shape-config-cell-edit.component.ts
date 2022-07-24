import { Component, OnInit, Input, Output, EventEmitter, SimpleChanges } from '@angular/core';
import { FormBuilder } from '@angular/forms';

@Component({
  selector: 'shape-config-cell-edit',
  templateUrl: './shape-config-cell-edit.component.html',
  styleUrls: ['./shape-config-cell-edit.component.scss']
})
export class ShapeConfigCellEditComponent implements OnInit {

  data: any = {}

  @Input() currentCellData: any = {
    rowIndex: '',
    colIndex: '',
    colName: '',
    nextColName: '',
    rowName: '',
    nextRowName: '',
    cellValue: '',
    rowData: ''
  };
  powerValEditPopup
  @Output() saveValue = new EventEmitter<object>();
  @Input() display = 'Quantity'

  constructor(private fb: FormBuilder) {
    this.powerValEditPopup = this.fb.group({ 'Quantity': [0], 'Price': [0] });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.currentCellData && changes.currentCellData.previousValue) {
      console.log(changes.currentCellData);
      if (this.display === 'All') {
        let values = changes.currentCellData.currentValue.cellValue.split('  |  ');
        this.powerValEditPopup.get('Quantity').setValue(values[0]);
        this.powerValEditPopup.get('Price').setValue(values[1]);
      } else {
        this.powerValEditPopup.get(this.display).setValue(changes.currentCellData.currentValue.cellValue);
      }
    }
    if (changes.display && changes.display.previousValue) {
      console.log(changes.display);
      console.log(this.display);
    }
  }

  ngOnInit() { }

  save() {
    console.log(this.powerValEditPopup.value);
    if (this.display === 'All') {
      this.saveValue.emit({
        rowIndex: this.currentCellData.rowIndex,
        colIndex: this.currentCellData.colIndex,
        attribute : this.display,
        Quantity : this.powerValEditPopup.value['Quantity'],
        Price : this.powerValEditPopup.value['Price']
      })
    } else {
      this.saveValue.emit({
        rowIndex: this.currentCellData.rowIndex,
        colIndex: this.currentCellData.colIndex,
        attribute : this.display,
        value: this.powerValEditPopup.value[this.display]
      })
    }
    this.currentCellData.overlaypanel.hide();
  }

  cancel() {
    this.currentCellData.overlaypanel.hide();
  }
}
