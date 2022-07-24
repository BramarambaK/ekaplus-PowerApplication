import { Component, OnInit, Input, Output, EventEmitter, SimpleChanges } from '@angular/core';

@Component({
  selector: 'days-picker',
  templateUrl: './days-picker.component.html',
  styleUrls: ['./days-picker.component.scss']
})
export class DaysPickerComponent implements OnInit {

  days = ['S','M','T','W','T','F','S','H'];
  daysText = ['Sunday','Monday','Tuesday','Wednesday','Thrusday','Friday','Saturday','Holiday'];
  selectedIndex = [true,true,true,true,true,true,true,true];
  @Input() existingDays
  @Output() selectedDays = new EventEmitter(); 

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.existingDays && changes.existingDays.currentValue) {
      let days = changes.existingDays.currentValue;
      this.daysText.forEach((day,index)=>{
        if(days[day]){
          this.selectedIndex[index] = true;
        }else{
          this.selectedIndex[index] = false;
        }
      })
    }
  }

  constructor() { }

  ngOnInit() { }
  
  addDayToBlock(i){
    this.selectedIndex[i] = !this.selectedIndex[i];
    this.selectedDays.emit({'day':this.daysText[i], 'selected':this.selectedIndex[i]});
  }

}
