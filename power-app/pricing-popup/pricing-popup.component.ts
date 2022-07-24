import { Component, OnInit, Input, SimpleChanges } from '@angular/core';
import { NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { HttpClient } from '@angular/common/http';
import { FormBuilder } from '@angular/forms';
import { PricingService } from '@app/views/Pricing/pricing-app/config.service';

@Component({
  selector: 'pricing-popup',
  templateUrl: './pricing-popup.component.html',
  styleUrls: ['./pricing-popup.component.scss']
})
export class PricingPopupComponent implements OnInit {
  @Input() formulaName;
  @Input() index;
  @Input() itemIndex;
  @Input() contractDetails;
  @Input() valuationField;
  @Input() DataForPricing;
  @Input() mdmPriceUnit
  ngOnInit() {
    this.formula = this.formulaName;
  }

  ngOnChanges(change:SimpleChanges) {
    if(change.formulaName){
      this.formula = change.formulaName.currentValue;
      console.log(this.formula);
    }
    if (change.index) {
      this.index = change.index.currentValue;
    }
  }

  closeResult: string;
  formula;
  constructor(
    private pricingConfigService: PricingService,
    private modalService: NgbModal,
    private fb: FormBuilder,
    private http: HttpClient
  ) { }

  open(content) {

    let currentItem = this.contractDetails.itemDetails[this.itemIndex];
    let errorMsg = "";
    if (!currentItem.deliveryFromDate || !currentItem.deliveryToDate) {
      errorMsg += " 'Delivery Period' "
    }
    if (!currentItem.pricing.payInCurId) {
      errorMsg += " 'Pay-In Settlement Currency' "
    }
    if (!currentItem.pricing.priceUnitId) {
      errorMsg += " 'Price Unit' "
    }

    if (errorMsg) {
      errorMsg = `Enter the following for Formula Pricing : ${errorMsg}`;
      //this.cs.reqFailedObs.observers = this.cs.reqFailedObs.observers.slice(-1);
      //this.cs.reqFailedObs.next(errorMsg);
    } else {
      this.modalService
        .open(content, {
          ariaLabelledBy: 'modal-basic-title',
          size: 'lg',
          windowClass: 'ContractPopup'
        })
        .result.then(
          result => {
            this.closeResult = `Closed with: ${result}`;
          },
          reason => {
            this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
          }
        );
    }


    this.pricingConfigService.changeCurrentComponent('listing');

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
}
