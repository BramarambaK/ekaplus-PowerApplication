import { Component, OnInit, Input, SimpleChanges, ViewChild } from '@angular/core';
import * as moment from 'moment';
//import { UtilService } from '@app/views/-Physicals/physicals-app/utils/util.service';
import { DeliveryDetailsService } from '../delivery-details.service';
import * as _ from 'lodash';
import { DeliveryPricingService } from '../delivery-pricing.service';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { map } from 'rxjs/operators';

@Component({
  selector: 'shape-details-table',
  templateUrl: './shape-details.component.html',
  styleUrls: ['./shape-details.component.scss']
})
export class ShapeDetailsComponent implements OnInit {

  blockDetailsGraph
  blockDetails : any = []
  blockDetailsKeys: string[];
  blockDetailsHeading;
  initialBlock
  @Input() productId
  @Input() contractRefNo
  @Input() isPopUp
  @Input() popUpTableDetails
  contractData
  priceUnitOptions
  pricingFormulaName : any = [];
  finalValidation = false;
  validation = []

  @ViewChild('priceError') priceErrorPopup;

  constructor(private http: HttpClient, private deliveryPricingService : DeliveryPricingService, private deliveryService: DeliveryDetailsService) { }

  ngOnInit() {
    this.initializeTable();
    this.initializePricingData();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.contractRefNo && changes.contractRefNo.currentValue) {
      this.getShapeDetailsInfo(changes.contractRefNo.currentValue);
    }
    if (changes.productId && changes.productId.currentValue) {
      this.fetchDropdownMDM(changes.productId.currentValue);
    }
  }

  initializeTable() {
    this.blockDetailsHeading = [
      { label: "S. No.", width: 80, key: 'blockNo' },
      { label: "Start Date", width: 100, key: 'startDate' },
      { label: "End Date", width: 100, key: 'endDate' },
      { label: "Time Frequency", width: 100, key: 'timeFrequency' },
      { label: "Quantity Unit", width: 100, key: 'quantityUnit'},
      { label: "Payment Settlement Currency", width: 100, key: "payInCurId" },
      { label: "Price Type", width: 120, key: "priceType" },
      { label: "Expression", width: 180, key: "priceExpression" },
      { label: "Price Unit", width: 100, key: "priceUnit" },
      { label: "Transmission Loss", width: 130, key: 'transmissionLoss' },
      { label: "Secondary Cost", width: 130, key: 'secondaryCost' },
      { label: "Shape", width: 180, key: 'shape' },
      { label: "Price", width: 120, key: 'price' },
    ]

    this.blockDetailsGraph = {
      startDate: { editable: true, type: 'datePicker' },
      endDate: { editable: true, type: 'datePicker' },
      timeFrequency: { editable: true, type: 'dropdown' },
      blockNo: { editable: false, type: 'text', calculationFunction: "" },
      quantityUnit: { editable: true, type: 'dropdown', options: [], changesColumn: [] },
      priceType: { editable: true, type: 'dropdown', options: [], changesColumn: [] },
      expression: { editable: false, type: 'expression' },
      priceExpression: { editable: false, type: 'priceExpression' },
      priceUnit: { editable: true, type: 'dropdown', options: [], changesColumn: [], calculationFunction: "loadingPriceUnits" },
      payInCurId: { editable: true, type: 'dropdown', options: [], changesColumn: ["priceUnit"] },
      transmissionLoss: { editable: false, type: 'popup' },
      secondaryCost: { editable: false, type: 'popup' },
      shape: { editable: false, type: 'shape-definition' },
      price: { editable: false, type: 'shape-price' }
    };

    this.initialBlock = {
      "startDate": "dd-mm-yyyy",
      "startDateDatePicker": "",
      "endDate": "dd-mm-yyyy",
      "endDateDatePicker": "",
      "timeFrequency": null,
      "timeFrequencyDisplayName": "-",
      "quantityUnit": null,
      "quantityUnitDisplayName": "-",
      "priceType": null,
      "priceTypeDisplayName": "-",
      "expression": "",
      "priceUnit": null,
      "priceUnitDisplayName": "-",
      "payInCurId": null,
      "payInCurIdDisplayName": "-",
      "transmissionLoss": "+ Add Loss",
      "secondaryCost": "+ Add Cost",
      "shape": "Configure",
      "price": "ShapePrice"
    }

    this.addBlock();
    this.popUpHideFields();
  }

  addBlock() {
    let blockLen = this.blockDetails.length;
    let blockNo
    if (blockLen <= 0) {
      blockNo = blockLen + 1;
    } else {
      blockNo = parseInt(this.blockDetails[blockLen - 1].blockNo) + 1;
    }
    this.initialBlock["blockNo"] = blockNo;
    this.blockDetails.push(this.initialBlock);
  }

  popUpHideFields(){
    this.blockDetailsHeading =  this.blockDetailsHeading.filter(obj=>{
      let hide = this.popUpTableDetails.hideFields.find(field => obj.key === field)
      if(!hide){
        return obj
      }
    });
    this.popUpTableDetails.hideFields.forEach(element => {
      delete this.initialBlock[element];
    });
  }

  popUpDefaults(){
    Object.keys(this.popUpTableDetails.values).forEach(element => {
      this.initialBlock[element] = this.popUpTableDetails.values[element];
      if(this.blockDetailsGraph[element].options){
        let option = this.blockDetailsGraph[element].options.find(option=>option.value === this.popUpTableDetails.values[element]);
        if(option){
          let displayColName = element+'DisplayName';
          this.initialBlock[displayColName] = option.label;
        }
      }
    })
  }

  getDatePickerDate(date) {
    if (date === 'dd-mm-yyyy') {
      return new Date();
    }
  }

  blockTableChange(index, block, columnName) {
    let columnsAffected = this.blockDetailsGraph[columnName].changesColumn;
    if(columnsAffected){
      columnsAffected.forEach(columnName => {
        let { calculationFunction } = this.blockDetailsGraph[columnName];
        this[calculationFunction](block, index);
      })
    }
    console.log(this.blockDetails);
    this.deliveryService.addBlockDetails(this.blockDetails);
  }

  blockTableDateChange(index, block, columnName) {
    let date = moment(block[columnName + 'DatePicker']).format('DD-MM-YYYY');
    block[columnName] = date;
    this.blockTableChange(index, block, columnName);
  }

  blockTableDropdownChange(index, block, columnName) {
    let displayColName = columnName+'DisplayName';
    let value = block[columnName];
    let option = this.blockDetailsGraph[columnName].options.find(option=>option.value === value);
    block[displayColName] = option.label;
    if(columnName === 'priceExpression'){
      block['expression'] = "";
    }
    this.blockTableChange(index, block, columnName);
  }

  loadingPriceUnits(block){
    let mdmPayload = [{ serviceKey: "productPriceUnit", dependsOn: [this.productId, block.payInCurId]}]
    this.deliveryService.getMDMdata(mdmPayload).pipe(
      map(res=>this.deliveryService.transform_MdmResponse_ForPdropdown(res))
    ).subscribe((res:any)=>{
      this.blockDetailsGraph['priceUnit'].options = res['productPriceUnit'];
    })
  }

  initializePricingData() {
    this.contractData = this.deliveryPricingService.contractData

    this.priceUnitOptions = this.deliveryPricingService.priceUnitOptions

    this.deliveryPricingService.formulaDetails.subscribe((data: any) => {
      if (_.get(this.deliveryPricingService.getPricingInvocationSource(), 'name', '') === 'blockFormulaPricing') {
        let blockRowIndex = this.deliveryPricingService.pricingInvocationSource.index
        this.pricingFormulaName[data[0]._id] = data[0].formulaName;
        this.blockDetails[blockRowIndex].expression = data[0]._id;
        this.deliveryService.addBlockDetails(this.blockDetails);
      }
    });

  }

  setPricingInvocation(blockIndex) {
    if(this.blockDetails[blockIndex].expression){
      this.contractData.itemDetails[0].pricing.pricingFormulaId = this.blockDetails[blockIndex].expression;
    }
    this.deliveryPricingService.setPricingInvocationSource({ name: 'blockFormulaPricing', index: blockIndex });
  }

  setShapeConfigDefails(event){
    this.blockDetails[event.index].shape = event.shape;
    console.log(this.blockDetails);
  }

  calculateShapePrice(blockIndex,blockData){
    let formulaPriceInvocationSource = {
      name : 'blockFormulaPricing',
      index : blockIndex
    }
    this.deliveryPricingService.calculateBlockFormulaPrice(formulaPriceInvocationSource,blockData).subscribe((res:any)=>{
      console.log(res);
      if(res.data.errors || res.data.errorMessage){
        let error = res.data.errorMessage || res.data.errors[0].error;
        this.priceErrorPopup.open(error);
      }else{
        this.blockDetails[blockIndex].formulaPrice = parseFloat(res.data.price.toFixed(2));
      }
    })
  }

  getShapeDetailsInfo(contractRefNo) {
    let workflowData = {
      "filterData":
      {
        "filter": [
          {
            "fieldName": "powerContractRefNo",
            "value": contractRefNo,
            "operator": "eq"
          }
        ]
      },
      "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      "workFlowTask": "powerItemlisting"
    };

    this.workflowApiCall(workflowData).subscribe((res: any) => {
      this.blockDetails = res.data.sort((a,b)=>a.blockNo-b.blockNo)
      if(this.blockDetails['priceType'] !== 'Fixed'){
        let expressions = res.data.map(block=>block.expression);
        this.deliveryService.getMultipleFormulaDetails(expressions).subscribe((res:any)=>{
          this.pricingFormulaName = res.data.reduce(function (formulaIdObj, currentFormula) {
            let formula = {}
            formula[currentFormula._id]  =  currentFormula.formulaName;
            return { ...formulaIdObj, ...formula }
          }, {})
          console.log(this.pricingFormulaName);
        })
      }
    })
  }

  workflowApiCall(workFlowData) {
    let httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this.http.post(`/workflow/data`, workFlowData, httpOptions)
  }

  validateShape(){
    let len = this.blockDetails.length;
    let headingLen = this.blockDetailsHeading.length;
    let invalid = false;
    for(let i=0;i<len;i++){
      this.validation[i] = [];
      for(let j=0;j<headingLen;j++){
        let key = this.blockDetailsHeading[j].key;
        if(key === 'startDate' || key === 'endDate'){
          if(this.blockDetails[i][key] === "dd-mm-yyyy"){
            this.validation[i][key] = true;
            invalid = true
          }else{
            this.validation[i][key] = false;
          }
        }else if(key === 'priceExpression'){
          if(this.blockDetails[i].priceType === 'FormulaPricing'){
            if(!this.blockDetails[i].expression || this.blockDetails[i].expression === ""){
               invalid = true;
               this.validation[i][key] = true;
            }
          }else{
            this.validation[i][key] = false;
          }
        }else if(key === 'shape'){
          if(this.blockDetails[i].priceType === 'FormulaPricing'){
            if(!(_.has(this.blockDetails[i].shape , ['contracted','Quality','fileName'])
               && _.has(this.blockDetails[i].shape , ['nominated','Quality','fileName'])
                  && _.has(this.blockDetails[i].shape , ['nominated','actuals','fileName']))){
                    invalid = true;
                    this.validation[i][key] = true;
                  }
          }else if(this.blockDetails[i].priceType === 'Fixed'){
            let tabs = ['contracted','nominated','actuals'];
            let attributes = ['Quantity', 'Price'];
            for(let k=0; k<2; k++){
              for(let l=0; l<3; l++){
                if(!(_.has(this.blockDetails[i].shape , [tabs[k],attributes[l],'fileName']))){
                  console.log(tabs[i] + ' does not contain '+attributes[i]+' file');
                  invalid = true;
                  this.validation[i][key] = true;
                  break
                }
              }
            }
          }
        }else{
          if(this.blockDetails[i][key]){
            this.validation[i][key] = false;
            invalid = true;
          }else{
            this.validation[i][key] = true;
          }
        }
      }
    }
    this.finalValidation = true;
    setTimeout(()=>{
      this.finalValidation = false;
    }, 4000);
    return invalid;
  }

  fetchDropdownMDM(productId){
    let mdmPayload = [
      {serviceKey : "physicalproductquantitylist", dependsOn : [productId] },
      {serviceKey : "productpricetypelist", dependsOn : [productId] },
      {serviceKey : "productCurrencyList", dependsOn: [productId]},
      {serviceKey : "productPriceUnit", dependsOn: [productId]},
      {serviceKey : "powerShapeTimeFrequency"}
    ]
    this.deliveryService.getMDMdata(mdmPayload).pipe(
      map(res=>this.deliveryService.transform_MdmResponse_ForPdropdown(res))
    ).subscribe((res:any)=>{
      this.blockDetailsGraph['quantityUnit'].options = res['physicalproductquantitylist'];
      //this.blockDetailsGraph['priceType'].options = res['productpricetypelist'];
      this.blockDetailsGraph['priceType'].options = [{ label: '-select-', value: '__empty__' },{label: "Fixed", value: "Fixed"},{label: "FormulaPricing", value: "FormulaPricing"}]
      this.blockDetailsGraph['payInCurId'].options = res['productCurrencyList'];
      this.blockDetailsGraph['priceUnit'].options = res['productPriceUnit'];
      this.blockDetailsGraph['timeFrequency'].options = res['powerShapeTimeFrequency'];
      this.popUpDefaults();
    })
  }

}

