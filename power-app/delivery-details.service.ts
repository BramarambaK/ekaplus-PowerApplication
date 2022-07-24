import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { map, delay } from 'rxjs/operators';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DeliveryDetailsService {

  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }

  generalDetails = {};
  blockDetails = [];
  shapeFilesSubject = new BehaviorSubject({
    actuals: {},
    contracted: {},
    nominated: {}
  });

  updateGeneralDetails(data) {
    this.generalDetails = data;
  }

  addBlockDetails(blockDetails) {
    this.blockDetails = blockDetails;
  }

  getGeneralDetails() {
    return this.generalDetails;
  }

  getBlockDetails() {
    return this.blockDetails;
  }

  getShapeConfigColumns(fileName) {
    let workflowPayload = {
      "task": "shape_columns",
      "workflowTaskName": "shape_columns",
      "appName": "power",
      "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      "output": { "shape_columns": {'fileName':fileName} },
      "payLoadData": ""
    }
    return this.http.post(`/workflow`, workflowPayload, this.httpOptions);
  }

  getShapeConfigData(shape_data) {
    let workflowPayload = {
      "task": "shape_data",
      "workflowTaskName": "shape_data",
      "appName": "power",
      "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      "output": { "shape_data": shape_data },
      "payLoadData": ""
    }
    return this.http.post(`/workflow`, workflowPayload, this.httpOptions);
  }

  updateShapeConfigData(body) {
    let workflowPayload = {
      "task": "shape_update",
      "workflowTaskName": "shape_update",
      "appName": "power",
      "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      "output": {
        "shape_update": body
      },
      "payLoadData": ""
    }
    return this.http.post(`/workflow`, workflowPayload, this.httpOptions);
  }

  uploadFileToS3FromUI(file) {
    const httpOptionsForDocument = {
      headers: new HttpHeaders({
        'storageType': 'awsS3'
      })
    };
    return this.http.post(`/upload`, file, httpOptionsForDocument);
  }

  uploadFileToFileSysFromUI(file) {
    const httpOptionsForDocument = {
      headers: new HttpHeaders({
        'storageType': 'fileSys'
      })
    };
    return this.http.post(`/upload`, file, httpOptionsForDocument);
  }


  updateFiletoS3FromBackend(file){
    return this.http.post(`/workflow`, file, this.httpOptions);
  }

  downloadFileFromS3(file) {
    const httpOptionsForDocument = {
      headers: new HttpHeaders({
        'storageType': 'awsS3',
        'folderInS3': 'powerDocs'
      })
    };
    return this.http.post(`/workflow`, file, httpOptionsForDocument);
  }

  shapeFileChange(data) {
    return this.http.post(`/workflow`, data);
  }

  getFormulaDetails(id) {
    let data = {
      "appId": "84d7b167-1d9f-406d-b974-bea406a25f9a",
      "workFlowTask": "formula_list"
    }
    return this.http.post('/workflow/data?_id='+id, data)
           .pipe(map((res:any)=>res.data));
  }

  getMultipleFormulaDetails(arr){
    let workflowData = {
      "filterData":
      {
        "filter": [
          {
            "fieldName": "_id",
            "value": arr,
            "operator": "in"
          }
        ]
      },
      "appId": "84d7b167-1d9f-406d-b974-bea406a25f9a",
      "workFlowTask": "formula_list"
    };
    return this.http.post('/workflow/data', workflowData);
  }

  deleteItem(item){
    let workflowData = {
      "workflowTaskName": "deletePowerContractItem",
      "task": "deletePowerContractItem",
      "appName": "power",
      "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      "output" : {
        "deletePowerContractItem" : item
      },
      "id" : item._id
    };
    return this.http.post('/workflow', workflowData);
  }

  
  getMDMdata(mdmData){
    let workFlowConfigBody = {
      appId : "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      workFlowTask: 'deliveryDetails_PNG',
      payLoadData: '',
      data : mdmData
    }
    return this.http.post(`/workflow/mdm`, workFlowConfigBody).pipe(delay(Math.floor(Math.random() * 1000)))
  }

  transform_MdmResponse_ForPdropdown(mdmData){
    let pDropdownData = {};
    for (const property in mdmData) {
      pDropdownData[property] = [];
      mdmData[property].forEach(element => {
        let _labelVal = {"label":element.value, "value":element.key}
        pDropdownData[property].push(_labelVal);
      })
      pDropdownData[property].unshift({ label: '---Select-----', value: '__empty__' });
    }
    console.log(pDropdownData);
    return pDropdownData;
  }

  getCollectionData() {
    let workflowPayload = {
      "task": "power_collection",
      "workFlowTask": "power_collection",
      "appName": "power",
      "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      "output": {
        "power_collection": {}
      },
      "payLoadData": {}
    }
    return this.http.post(`/workflow/data`, workflowPayload, this.httpOptions);
  }

  copyFile(data){
    let workflowPayload = {
      "task": "shape_copyFile",
      "workflowTaskName": "shape_copyFile",
      "appName": "power",
      "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      "output": {
        "shape_copyFile": data
      },
      "payLoadData": ""
    }
    return this.http.post(`/workflow`, workflowPayload, this.httpOptions);
  }

  getContractGeneralDetails(contractRefNo='PW-68-REF') {
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
      "workFlowTask": "powerlisting"
    };
    let httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this.http.post(`/workflow/data`, workflowData, httpOptions)
  }

}
