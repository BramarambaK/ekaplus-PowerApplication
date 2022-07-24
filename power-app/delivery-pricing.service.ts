import { Injectable } from '@angular/core';
import { PricingService } from '@app/views/Pricing/pricing-app/config.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map, concatMap, tap, switchMap } from 'rxjs/operators';
import { of, BehaviorSubject } from 'rxjs';
import { DeliveryDetailsService } from './delivery-details.service';

@Injectable({
  providedIn: 'root'
})
export class DeliveryPricingService {

  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  contractData
  priceUnitOptions
  pricingInvocationSource
  formulaDetails = new BehaviorSubject(null);
  formulaDetailsByPricingInvocationSource : any = { 'blockFormulaPricing': [] };

  constructor(private pricingConfigService: PricingService, private http: HttpClient, private deliveryService: DeliveryDetailsService) {

    this.contractData = {
      "itemDetails": [
        {
          "productId": "PDM-4721",
          "itemQty": 1200,
          "itemQtyUnitId": "QUM-M-8",
          "pricing": {
            "priceTypeId": "FormulaPricing",
            "pricingFormulaId": null,
            "priceUnit": "USD/MT",
            "priceUnitId": "PPU-7152",
            "payInCurId": "CM-M-7"
          },
          "deliveryFromDate": {
            "date": {
              "year": 2019,
              "month": 11,
              "day": 11
            },
            "jsdate": "2019-11-10T18:30:00.000Z",
            "formatted": "11-Nov-2019",
            "epoc": 1573410600
          },
          "deliveryToDate": {
            "date": {
              "year": 2019,
              "month": 11,
              "day": 28
            },
            "jsdate": "2019-11-27T18:30:00.000Z",
            "formatted": "28-Nov-2019",
            "epoc": 1574879400
          }
        }
      ],
      "_id": "12345"
    }

    this.priceUnitOptions = [
      {
        "key": "PPU-7152",
        "value": "USD/MT"
      }
    ]

    this.getPriceDetails();

  }

  setPricingInvocationSource(val){
    this.pricingInvocationSource = val;
  }

  getPricingInvocationSource(){
    return this.pricingInvocationSource;
  }

  getPriceDetails() {
    console.log(' ================== subscribed to pricing changes ================= ');
    this.pricingConfigService.contractFormula
      .pipe(
        tap(res => console.log(res)),
        switchMap((formulaId: any) => {
          console.log(formulaId);
          if (formulaId) {
            let data = {
              "appId": "84d7b167-1d9f-406d-b974-bea406a25f9a",
              "workFlowTask": "formula_list"
            }
            return this.http.post('/workflow/data?_id=' + formulaId, data).pipe(map((res: any) => res.data))
          } else {
            return of(null);
          }
        })
      ).subscribe(res => {
        console.log(res);
        if(res){
          let pricingInvocationSource_Name = this.getPricingInvocationSource().name;
          if (pricingInvocationSource_Name === 'blockFormulaPricing') {
            let blockIndex = this.pricingInvocationSource.index;
            this.formulaDetailsByPricingInvocationSource['blockFormulaPricing'][blockIndex] = res;
          } else {
            this.formulaDetailsByPricingInvocationSource[pricingInvocationSource_Name] = res;
          }
          this.formulaDetails.next(res);
        }
      })
  }

  getFormulaDetails(formulaPriceInvocationSource) {
    console.log(formulaPriceInvocationSource);
    console.log(this.formulaDetailsByPricingInvocationSource);
    if (formulaPriceInvocationSource.name === 'blockFormulaPricing') {
      let blockIndex = formulaPriceInvocationSource.index;
      return this.formulaDetailsByPricingInvocationSource['blockFormulaPricing'][blockIndex];
    } else {
      return this.formulaDetailsByPricingInvocationSource[formulaPriceInvocationSource.name];
    }
  }

  calculateBlockFormulaPrice(formulaPriceInvocationSource,blockData) {
    let formulaDetails = this.getFormulaDetails(formulaPriceInvocationSource);
    let generalDetails = this.deliveryService.getGeneralDetails();
    generalDetails['valuationFormulaDetails'] = this.getFormulaDetails({name:'valuationFormula'});
    console.log(generalDetails);
    let contractData = {
      ...blockData,
      generalDetails,
      formulaDetails
    }
    console.log(contractData);
    let httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'host': '7es0je4527.execute-api.us-east-2.amazonaws.com',
        'hostName': '7es0je4527.execute-api.us-east-2.amazonaws.com'
      })
    };
    let payload = {
      "task": "block_price",
      "workflowTaskName": "block_price",
      "appName": "power",
      "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      "payLoadData": "",
      "output" : { "block_price": contractData }
    }
    console.log(payload);
    return this.http.post(`/workflow`, payload, httpOptions);
  }

}
