import { Component, OnInit, Input, SimpleChanges, ViewChild } from '@angular/core';
import * as moment from 'moment';
import { PricingService } from '@app/views/Pricing/pricing-app/config.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { DeliveryDetailsService } from '../delivery-details.service';
import * as _ from 'lodash';
import { DeliveryPricingService } from '../delivery-pricing.service';

@Component({
  selector: 'block-details-table',
  templateUrl: './block-details.component.html',
  styleUrls: ['./block-details.component.scss']
})
export class BlockDetailsComponent implements OnInit {

  blockDetailsGraph
  blockDetails = [];
  blockDetailsKeys: string[];
  blockDetailsHeading;
  initialBlock

  contractData
  priceUnitOptions
  pricingTriggerFor: any;
  pricingFormulaName: any = [];
  grandTotal = {};
  validation = [];
  finalValidation = false;
  //currency

  @Input() priceType = 'Fixed';
  @Input() contractRefNo
  @Input() productId
  @Input() isPopUp
  @Input() popUpTableDetails

  @ViewChild('priceError') priceErrorPopup;

  constructor(private deliveryPricingService: DeliveryPricingService, private deliveryService: DeliveryDetailsService, private http: HttpClient, private pricingConfigService: PricingService) { }

  ngOnInit() {
    this.initializeTable();
    this.initializePricingData();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.contractRefNo && changes.contractRefNo.currentValue) {
      this.getBlockDetailsInfo(changes.contractRefNo.currentValue);
    }
    // if (changes.priceType && changes.priceType.previousValue) {
    //   this.priceType = changes.priceType.currentValue;
    //   this.blockDetails = [];
    //   this.addBlock();
    // }
    if (changes.productId && changes.productId.currentValue) {
      this.fetchDropdownMDM(changes.productId.currentValue);
    }
  }

  initializeTable() {
    this.blockDetailsHeading = [
      { label: "S. No.", width: 70, key: 'blockNo', validate: false },
      { label: "Start Date", width: 100, key: 'startDate', validate: true },
      { label: "End Date", width: 100, key: 'endDate', validate: true },
      { label: "Start Time", width: 100, key: 'startTime', validate: true },
      { label: "End Time", width: 100, key: 'endTime', validate: true },
      { label: "Time Frequency", width: 120, key: 'timeFrequency', validate: true },
      { label: "Days", width: 220, key: 'weekDays', validate: true },
      { label: "Quantity", width: 100, key: 'quantity', validate: true },
      { label: "Quantity Unit", width: 100, key: 'quantityUnit', validate: true },
      { label: "Payment Settlement Currency", width: 100, key: "payInCurId", validate: true },
      { label: "Price Unit", width: 100, key: "priceUnit", validate: true },
      { label: "Price Type", width: 120, key: "priceType", validate: true },
      { label: "Price/Expression", width: 180, key: "priceExpression", validate: true },
      { label: "Transmission Loss", width: 150, key: 'transmissionLoss', validate: false },
      { label: "Secondary Cost", width: 150, key: 'secondaryCost', validate: false },
      { label: "Hours/Day", width: 100, key: 'hoursPerDay', validate: false },
      { label: "Quantity/Day", width: 100, key: 'quantityPerDay', validate: false },
      { label: "Total Days", width: 100, key: 'totalDays', validate: false },
      { label: "Total Hours", width: 100, key: 'totalHours', validate: false  },
      { label: "Total Quantity", width: 100, key: 'totalQuantity', validate: false  },
      { label: "Total Amount", width: 100, key: 'totalAmount', validate: false },
      { label: "Action", width: 100, key: 'action', validate: false }
    ]

    this.blockDetailsGraph = {
      startDate: { editable: true, type: 'datePicker', changesColumn: ["totalDays", "totalHours", "totalQuantity", "totalAmount"] },
      endDate: { editable: true, type: 'datePicker', changesColumn: ["totalDays", "totalHours", "totalQuantity", "totalAmount"] },
      weekDays: { editable: false, type: 'dayPicker', changesColumn: ["totalDays", "totalHours", "totalQuantity", "totalAmount"] },

      startTime: { editable: true, type: 'timePicker', changesColumn: ["hoursPerDay", "totalHours", "quantityPerDay", "totalQuantity", "totalAmount"] },
      endTime: { editable: true, type: 'timePicker', changesColumn: ["hoursPerDay", "totalHours", "quantityPerDay", "totalQuantity", "totalAmount"] },
      timeFrequency: { editable: true, type: 'dropdown', options: [], changesColumn: [] },

      quantity: { editable: true, type: 'input', changesColumn: ["quantityPerDay", "totalQuantity", "totalAmount"] },
      quantityUnit: { editable: true, type: 'dropdown', options: [], changesColumn: [] },
      priceType: { editable: true, type: 'dropdown', options: [], changesColumn: [] },
      price: { editable: true, type: 'input', changesColumn: ["totalAmount"] },
      expression: { editable: false, type: 'expression' },
      priceExpression: { editable: false, type: 'priceExpression' },
      priceUnit: { editable: true, type: 'dropdown', options: [], changesColumn: [], calculationFunction: "loadingPriceUnits" },
      payInCurId: { editable: true, type: 'dropdown', options: [], changesColumn: ["priceUnit"] },

      totalDays: { editable: false, type: 'text', calculationFunction: "calculateTotalDays" },
      quantityPerDay: { editable: false, type: 'text', calculationFunction: "calculateQuantityPerDay" },
      hoursPerDay: { editable: false, type: 'text', calculationFunction: "calculateHoursPerDay" },
      totalHours: { editable: false, type: 'text', calculationFunction: "calculateTotalHours" },
      totalQuantity: { editable: false, type: 'text', calculationFunction: "calcualteTotalQuantity" },
      totalAmount: { editable: false, type: 'text', calculationFunction: "calculateTotalAmount" },
      formulaPrice: { editable: false, type: 'formulaPrice' },
      
      blockNo: { editable: false, type: 'text', calculationFunction: "" },

      transmissionLoss: { editable: false, type: 'text' },
      secondaryCost: { editable: false, type: 'text' },

      action: { editable: false, type: 'action' }

    };

    this.initialBlock = {
      "startDate": "dd-mm-yyyy",
      "startDateDatePicker": "",
      "endDate": "dd-mm-yyyy",
      "endDateDatePicker": "",
      "startTime": "hh:mm",
      "startTimeTimePicker": "",
      "endTime": "hh:mm",
      "endTimeTimePicker": "",
      "timeFrequency": "60",
      "timeFrequencyDisplayName": "hourly",
      "weekDays": { 'Sunday': true, 'Monday': true, 'Tuesday': true, 'Wednesday': true, 'Thrusday': true, 'Friday': true, 'Saturday': true, 'Holiday': true },
      "quantity": 0,
      "quantityUnit": null,
      "quantityUnitDisplayName": "-",
      "priceType": null,
      "priceTypeDisplayName": "-",
      "price": 0,
      "expression": "",
      "priceUnit": null,
      "priceUnitDisplayName": "-",
      "payInCurId": null,
      "payInCurIdDisplayName": "-",
      "transmissionLoss": "+ Add Loss",
      "secondaryCost": "+ Add Cost",
      "hoursPerDay": 0,
      "quantityPerDay": 0,
      "totalDays": 0,
      "totalHours": 0,
      "totalQuantity": 0,
    }

    this.popUpHideFields();
    this.addBlock();

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

  calculateHoursPerDay(block, index) {
    let startTime = moment(block.startTime, "HH:mm:ss")
    let endTime = moment(block.endTime, "HH:mm:ss")
    let duration = moment.duration(endTime.diff(startTime));
    let hours = duration.asHours();
    block.hoursPerDay = parseFloat(hours.toFixed(2));
  }

  calculateQuantityPerDay(block) {
    block.quantityPerDay = block.quantity * block.hoursPerDay;
  }

  calculateTotalDays(block) {
    block.totalDays = this.calculateNumberWeekDays(block);
    this.calculateGrandTotal('totalDays');
  }

  calculateTotalHours(block) {
    block.totalHours = parseFloat((block.hoursPerDay * block.totalDays).toFixed(2));
    this.calculateGrandTotal('totalHours');
  }

  calcualteTotalQuantity(block) {
    block.totalQuantity = parseFloat((block.quantityPerDay * block.totalDays).toFixed(2));
    this.calculateGrandTotal('totalQuantity');
  }

  calculateTotalAmount(block) {
    if (block.priceType === 'Fixed') {
      block.totalAmount = parseFloat((block.totalQuantity * block.price).toFixed(2));
      this.calculateGrandTotal('totalAmount');
    }
  }

  loadingPriceUnits(block){
    let mdmPayload = [{ serviceKey: "productPriceUnit", dependsOn: [this.productId, block.payInCurId]}]
    this.deliveryService.getMDMdata(mdmPayload).pipe(
      map(res=>this.deliveryService.transform_MdmResponse_ForPdropdown(res))
    ).subscribe((res:any)=>{
      this.blockDetailsGraph['priceUnit'].options = res['productPriceUnit'];
    })
  }

  // removeAddPrice(block){
  //   if (block.priceType === 'Fixed') {
  //     delete block['expression'];
  //     block['price'] = 0;
  //   } else if(block.priceType === "FormulaPricing"){
  //     delete block['price'];
  //     block['expression']
  //   }
  // }

  blockTableChange(index, block, columnName) {
    if(this.blockDetailsGraph[columnName].type === 'input' && block[columnName] === null){
      block[columnName] = 0;
    }
    let columnsAffected = this.blockDetailsGraph[columnName].changesColumn;
    columnsAffected.forEach(columnName => {
      let { calculationFunction } = this.blockDetailsGraph[columnName];
      this[calculationFunction](block, index);
    })
    console.log(this.blockDetails);
    this.deliveryService.addBlockDetails(this.blockDetails);
  }

  blockTableDateChange(index, block, columnName) {
    let date = moment(block[columnName + 'DatePicker']).format('DD-MM-YYYY');
    block[columnName] = date;
    this.blockTableChange(index, block, columnName);
  }

  blockTableTimeChange(index, block, columnName) {
    let date = moment(block[columnName + 'TimePicker']).format('HH:mm');
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

  initializePricingData() {

    this.contractData = this.deliveryPricingService.contractData

    this.priceUnitOptions = this.deliveryPricingService.priceUnitOptions

    this.deliveryPricingService.formulaDetails
    .subscribe((data: any) => {
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

  selectedBlockDays(event, blockIndex) {
    this.blockDetails[blockIndex]['weekDays'][event.day] = event.selected;
    this.blockTableChange(blockIndex, this.blockDetails[blockIndex], 'weekDays');
  }

  calculateNumberWeekDays(block) {
    let numberOfDays = 0;
    let dayIndexRef = {
      'Sunday': 0,
      'Monday': 1,
      'Tuesday': 2,
      'Wednesday': 3,
      'Thrusday': 4,
      'Friday': 5,
      'Saturday': 6,
      'Holiday': 7
    };
    let selectedDays = [];
    for (let [key, value] of Object.entries(block.weekDays)) {
      let dayIndex = dayIndexRef[key];
      value ? selectedDays[dayIndex] = 1 : selectedDays[dayIndex] = 0;
    }
    if (block.startDate && block.endDate) {
      let startDay = moment(block.startDate, "DD-MM-YYYY");
      let endDay = moment(block.endDate, "DD-MM-YYYY");
      while (startDay.isSameOrBefore(endDay)) {
        if (selectedDays[startDay.day()]) {
          numberOfDays += 1;
        }
        startDay.add(1, 'days');
      }
    }
    return numberOfDays;
  }

  deleteRow(index) {
    if(this.blockDetails[index]._id){
      this.deliveryService.deleteItem(this.blockDetails[index]).subscribe(res=>{
        this.blockDetails.splice(index, 1);
      })
    }else{
      this.blockDetails.splice(index, 1);
    }
  }

  calculateGrandTotal(key) {
    let total = this.blockDetails.reduce(function (acc, block) { return acc + parseFloat(block[key]); }, 0)
    this.grandTotal[key] = parseFloat(total.toFixed(2));
  }

  getBlockDetailsInfo(contractRefNo) {
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
      //if(this.priceType !== 'Fixed'){
        let expressions = res.data.map(block=>block.expression);
        this.deliveryService.getMultipleFormulaDetails(expressions).subscribe((res:any)=>{
          this.pricingFormulaName = res.data.reduce(function (formulaIdObj, currentFormula) {
            let formula = {}
            formula[currentFormula._id]  =  currentFormula.formulaName;
            return { ...formulaIdObj, ...formula }
          }, {})
          console.log(this.pricingFormulaName);
        })
      //}
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

  getMinDate(key, data) {
    if (key === 'endDate') {
      return moment(data.startDate, 'DD-MM-YYYY').toDate();
    }
    return null
  }

  getMinTime(key, data) {
    if (key === 'endTime') {
      let min = moment(data.startTime, 'HH:mm').toDate();
      return min;
    }
    return null
  }

  calculateFormualaPrice(blockIndex,blockData){
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

  validateBlock(){
    let len = this.blockDetails.length;
    let headingLen = this.blockDetailsHeading.length;
    let invalid = false;
    for(let i=0;i<len;i++){
      this.validation[i] = [];
      for(let j=0;j<headingLen;j++){
        let key = this.blockDetailsHeading[j].key;
        if(key === 'startDate' || key === 'endDate'){
          if(this.blockDetails[i][key] === "dd-mm-yyyy" || this.blockDetails[i][key] === "Invalid date"){
            this.validation[i][key] = true;
            invalid = true
          }else{
            this.validation[i][key] = false;
          }
        }else if(key === 'startTime' || key === 'endTime'){
          if(this.blockDetails[i][key] === "hh:mm" || this.blockDetails[i][key] === "Invalid date"){
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
            }else{
              this.validation[i][key] = false;
            }
          }else if(this.blockDetails[i].priceType === 'Fixed'){
            if(!this.blockDetails[i].price || this.blockDetails[i].price === 0){
              invalid = true;
              this.validation[i][key] = true;
            }else{
              this.validation[i][key] = false;
            }
          }
        }else if(this.blockDetailsHeading[j].validate){
          if(this.blockDetails[i][key]){
            this.validation[i][key] = false;
          }else{
            invalid = true;
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
      {serviceKey : "productPriceUnit", dependsOn: [this.productId]},
      {serviceKey : "powerBlockTimeFrequency"},
    ]
    this.deliveryService.getMDMdata(mdmPayload).pipe(
      map(res=>this.deliveryService.transform_MdmResponse_ForPdropdown(res))
    ).subscribe((res:any)=>{
      this.blockDetailsGraph['quantityUnit'].options = res['physicalproductquantitylist'];
      //this.blockDetailsGraph['priceType'].options = res['productpricetypelist'];
      this.blockDetailsGraph['priceType'].options = [{ label: '-select-', value: '__empty__' },{label: "Fixed", value: "Fixed"},{label: "FormulaPricing", value: "FormulaPricing"}]
      this.blockDetailsGraph['payInCurId'].options = res['productCurrencyList'];
      this.blockDetailsGraph['priceUnit'].options = res['productPriceUnit'];
      this.blockDetailsGraph['timeFrequency'].options = res['powerBlockTimeFrequency'];
      this.popUpDefaults();
    })
  }

}

