import { Component, OnInit, Input } from '@angular/core';
import { NgbModalConfig, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { PricingService } from '@app/views/Pricing/pricing-app/config.service';

@Component({
  selector: 'app-formula-details-popup',
  templateUrl: './formula-details-popup.component.html',
  styleUrls: ['./formula-details-popup.component.scss'],
  providers: [NgbModalConfig, NgbModal]
})
export class FormulaDetailsPopupComponent implements OnInit {
  @Input() DataForPricing;
  @Input() formulaName;
  @Input() index;
  @Input() contractDetails;
  @Input() valuationField;
  @Input() itemIndex;
  @Input() mdmPriceUnit;
  constructor(
    config: NgbModalConfig,
    private modalService: NgbModal,
    private pricingConfigService: PricingService
  ) {
    config.backdrop = 'static';
    config.keyboard = false;
  }

  ngOnInit() { }

  open(content) {
    this.modalService.open(content, {
      windowClass: 'ContractPopup'
    });
    this.pricingConfigService.changeCurrentComponent('formulaForm');
  }
}
