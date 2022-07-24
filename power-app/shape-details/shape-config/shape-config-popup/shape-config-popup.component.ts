import { Component, OnInit, Input, SimpleChanges, Output, EventEmitter, ViewEncapsulation } from '@angular/core';
import { NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { DeliveryDetailsService } from '../../../delivery-details.service';
import { FormBuilder } from '@angular/forms';
import * as _ from 'lodash';

@Component({
  selector: 'shape-config-popup',
  templateUrl: './shape-config-popup.component.html',
  styleUrls: ['./shape-config-popup.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class ShapeConfigPopupComponent implements OnInit {
  @Input() shapeDetails
  @Input() shapeIndex
  @Input() priceType
  closeResult
  tabOptions = ['contracted','nominated','actuals']
  tabValue = 'contracted'
  tabIndexMap = {
    'contracted' : 0,
    'nominated' : 1,
    'actuals' : 2
  }
  @Output() shapeConfig = new EventEmitter<object>();
  loading = false

  constructor(private fb: FormBuilder, private modalService: NgbModal, private deliveryService: DeliveryDetailsService) { }

  ngOnInit() { }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.priceType) {
      this.priceType = changes.priceType.currentValue;
    }
    if (changes.shapeDetails && changes.shapeDetails.previousValue) {
      this.shapeDetails = changes.shapeDetails.currentValue.shape;
    }
  }

  open(content) {
    console.log(this.shapeDetails);
    this.tabValue = this.tabOptions[0];
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title', size: 'lg', windowClass: 'ContractPopup' })
      .result.then((result) => {
        this.closeResult = `Closed with: ${result}`;
      }, (reason) => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      });
  }

  handleTabChange(e) {
    let previousTab = this.tabOptions[e.index-1];
    let currentTab = this.tabOptions[e.index];
    this.tabValue = this.tabOptions[e.index];
    if(previousTab && _.has(this.shapeDetails,['shape',previousTab])){
      let dropdowns = this.getDropdowns();
      let len = dropdowns.length;
      for(let i=0; i<len; i++){
        if (_.has(this.shapeDetails, ['shape',previousTab,dropdowns[i]]) && !_.has(this.shapeDetails, ['shape',currentTab,dropdowns[i]])) {
          let copy_file = this.shapeDetails.shape[previousTab][dropdowns[i]].fileName;
          let copyAPIdata = {
            'copy_from' : { 'fileName' : copy_file },
            'copy_to' : {
              'tab' : currentTab,
              'dropdown' : dropdowns[i]
            }
          }
          this.deliveryService.copyFile(copyAPIdata).subscribe((res:any)=>{
             let { tab, dropdown, fileName } = res.data;
             this.shapeDetails.shape[tab][dropdown] = { 'fileName' : fileName };
             this.shapeDetails['index'] = this.shapeIndex;
             this.shapeConfig.emit(this.shapeDetails); 
             this.deliveryService.shapeFilesSubject.next(this.shapeDetails.shape);
          })
        } 
      }
    }   
  }

  getDropdowns(){
    if (this.priceType === 'Fixed') {
      return ['Quantity','Price']
    } else {
      return ['Quantity']
    }
  }

  private getDismissReason(reason: any): string {
    if (reason === ModalDismissReasons.ESC) {
      return 'by pressing ESC';
    } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
      return 'by clicking on a backdrop';
    } else {
      return `with: ${reason}`;
    }
  }

  updateShapeConfig(shapeConfig){
    console.log("--- shapeConfig passed from table to popup ---");
    console.log(shapeConfig);
    this.shapeDetails.shape = shapeConfig.shape;
    this.shapeConfig.emit(shapeConfig);
  }

  saveShapeConfig(modal){
    console.log(this.shapeDetails);
    this.loading = true;
    if(Object.keys(this.shapeDetails.shape).length > 0){
      let data = {
        "task": "shape_file_uploadToS3",
        "workflowTaskName": "shape_file_uploadToS3",
        "appName": "power",
        "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
        "payLoadData": "",
        "output": {
          "shape_file_uploadToS3": this.shapeDetails.shape
        }
      }
      this.deliveryService.updateFiletoS3FromBackend(data).subscribe((res:any)=>{
        console.log(res);
        this.shapeDetails.shape = res.data;
        this.shapeConfig.emit({shape: res.data, index: this.shapeIndex});
        this.loading = false;
        modal.close('Save click');
      })
    }else{
      this.loading = false;
      modal.close('Save click');
    }
  }

}
