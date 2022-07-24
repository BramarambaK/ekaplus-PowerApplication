import { Component, OnInit, HostListener, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApplicationService } from '@app/views/application/application.service';
import { FormBuilder, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { concatMap } from 'rxjs/operators';
import { DeliveryDetailsService } from './delivery-details.service';
import * as _ from 'lodash';
import { DeliveryPricingService } from './delivery-pricing.service';
import { forkJoin, of } from 'rxjs';

@Component({
  selector: 'deliveryDetailsComponent',
  templateUrl: './deliveryDetails.power.component.html',
  styleUrls: ['./deliveryDetails.power.component.scss']
})

export class DeliveryDetails implements OnInit {

  workflowName: string = '';
  workFlowdata: any;
  appName: string;
  appMeta;
  objectName: string;
  metafields: any = {};
  layout: any;
  header: any;
  workFlowFields
  dropDowns: {};
  product
  enterWorkflow: boolean = false;
  outcome: boolean;
  error: any;
  selected: any;
  showLoader: boolean = true;
  deliveryDetailsForm
  contractData
  priceUnitOptions
  pricingFormulaName
  powerContractRefNo
  isEdit: boolean = false;
  finalValidation = false;
  displayValues = {};
  errorMsg = '';
  showWarning = false;
  @ViewChild('contractSavePopup') contractSavePopup;
  @HostListener('window:beforeunload', ['$event']) unloadHandler(event: Event) {
    event.returnValue = false;
  }
  apiCalled = false;
  @ViewChild('shapeTable') shapeTable
  @ViewChild('blockTable') blockTable
  queryParams
  isPopUp
  popUpGeneralDetails:any = { values : {}, hideFields : [], disableFields : [] };
  popUpTableDetails:any = { values : {}, hideFields : [], disableFields : [] };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private fb: FormBuilder,
    private appService: ApplicationService,
    private http: HttpClient,
    private deliveryService: DeliveryDetailsService,
    private deliveryPricingService: DeliveryPricingService
  ) { }

  ngOnInit() {
    this.appService.selected.subscribe((selected: any) => {
      if (!this.enterWorkflow) {
        this.selected = selected;
        console.log(this.selected);
      }
    });
    this.workFlowdata = this.appService.workFlowData;
    this.appService.appMeta$.subscribe(app => {
      this.appMeta = app;
    });
    // this.appService.showLoader$.subscribe((res: boolean) => {
    //   this.showLoader = res;
    // })
    this.route.paramMap.subscribe(params => {
      this.appName = params.get('app');
      this.objectName = params.get('objectName');
      this.workflowName = params.get('workflow');
      console.log(this.route.snapshot.queryParams);
      this.queryParams = this.route.snapshot.queryParams
      this.route.queryParams.subscribe(params => {
        console.log('------- the query params are -----------');
        console.log(params);
        this.queryParams = params;
        if(this.queryParams.isPopUp){
          this.isPopUp = this.queryParams.isPopUp;
        }
        if(this.queryParams.popUpGeneralDetails){
          this.popUpGeneralDetails = JSON.parse(this.queryParams.popUpGeneralDetails);
        }
        if(this.queryParams.popUpTableDetails){
          this.popUpTableDetails = JSON.parse(this.queryParams.popUpTableDetails);
        }
      });
      // needs loader correction
      this.appService.setLoaderState({ type: 'packaging-workflow', value: true });
      this.appService.getWorkFlowConfig(this.appMeta.sys__UUID, this.workflowName)
        .subscribe((res: any) => {
          this.appService.setLoaderState({ type: 'packaging-workflow', value: false });
          this.appService.workFlowData.storage = {
            ...res.flow[this.workflowName],
            workFlowTask: this.workflowName,
            objectMeta: res['objectMeta']
          };
          this.workFlowdata = this.appService.workFlowData;
          this.workFlowFields = res.flow[this.workflowName].fields;
          this.metafields = res['objectMeta'].fields;
          this.appService.setWorkflow(res.flow[this.workflowName]);
          this.header = this.appService.workFlowData.storage.fields;
          this.layout = this.appService.workFlowData.storage.layout;
          this.outcome = true;
          this.createFormGroup();
          this.filterDropdowns();
          this.hookDependants();
          this.showLoader = false;
        }
          , err => {
            this.appService.setLoaderState({ type: 'packaging-workflow', value: false });
            this.appService.showError(err);
          });
    });
    this.initializePricingData();
  }

  get deliveryType() {
    if (this.deliveryDetailsForm) {
      return this.deliveryDetailsForm.get('deliveryType').value;
    }
    return
  }

  createFormGroup() {
    let fields = this.workFlowFields.flat();
    let _formControls = fields.reduce((acc, curr) => {
      let newControl = {};
      newControl[curr.key] = [null, Validators.required];
      return { ...newControl, ...acc };
    }, {})
    console.log(_formControls);
    //_formControls['valuationFormulaId'] = [Validators.required];
    this.deliveryDetailsForm = this.fb.group(_formControls);
    console.log('the delivery details form is as :')
    console.log(this.deliveryDetailsForm);
    this.deliveryDetailsForm.get('product').valueChanges.subscribe(val => {
      this.product = val;
    })
    if (_.get(this.selected, 'selected.workflow_updateGeneralDetails_PNG', false)) {
      let deliveryDetails = this.selected.selected['workflow_updateGeneralDetails_PNG'];
      this.initializeEditFlow(deliveryDetails)
    } else if (_.get(this.selected, 'selected.powerlisting.powerContractRefNo', false)) {
      let deliveryDetails = this.selected.selected['powerlisting'];
      this.initializeEditFlow(deliveryDetails)
    } else if (this.queryParams.isPopUp === 'true'){
      if(this.queryParams.isEdit === 'true'){
        this.deliveryService.getContractGeneralDetails(this.queryParams.powerContractRefNo).subscribe((res:any)=>{
          console.log('--- general details of the contract are -----')
          console.log(res);
          let deliveryDetails = res.data[0];      
          this.isEdit = this.queryParams.isEdit
          this.selected.selected = { 'workflow_updateGeneralDetails_PNG' : { ...deliveryDetails, ...this.popUpGeneralDetails.values} }
          this.initializeEditFlow(deliveryDetails)
          this.hookDependants();
        })
      }else{
        this.selected.selected = { 'createTrade_PNG' : { ...this.popUpGeneralDetails.values } }
        this.hookDependants();
      }
    }
    this.deliveryDetailsForm.valueChanges.subscribe(res => {
      if (!this.isEdit) {
        this.getGeneralDetails('createTrade_PNG');
      } else {
        this.getGeneralDetails('workflow_updateGeneralDetails_PNG');
      }
    })
    if(this.popUpGeneralDetails.values){
      this.deliveryDetailsForm.patchValue(this.popUpGeneralDetails.values);
    }
    // if(this.popUpGeneralDetails.hideFields){
    //   this.popUpGeneralDetails.hideFields.forEach(field => {
    //     this.deliveryDetailsForm.removeControl(field);
    //   });
    // }
    if(this.popUpGeneralDetails.disableFields){
      this.popUpGeneralDetails.disableFields.forEach(field => {
        this.deliveryDetailsForm.get(field).disable();
      });
    }
  }

  initializeEditFlow(deliveryDetails) {
    this.isEdit = true;
    if (deliveryDetails.valuationFormulaId) {
      this.onLoadSetValuationFormulaDetails(deliveryDetails.valuationFormulaId);
    }
    this.deliveryDetailsForm.patchValue(deliveryDetails);
    this.powerContractRefNo = this.selected.selected['powerlisting']['powerContractRefNo'];
    //this.deliveryDetailsForm.disable();
  }

  filterDropdowns() {
    let fields = this.workFlowFields.flat().map(obj => obj.key).filter(
      field => {
        let fieldDetails = this.metafields[field]
        return (fieldDetails.serviceKey && !fieldDetails.parent)
      })
    let mdmPayloadData = [];
    fields.forEach(field => {
      mdmPayloadData.push({
        "serviceKey": this.metafields[field].serviceKey
      });
    });
    this.deliveryService.getMDMdata(mdmPayloadData).subscribe(res => {
      fields.forEach(field => {
        let serviceKey = this.metafields[field].serviceKey;
        this.metafields[field].options = res[serviceKey];
      });
      this.fetchCollectionData();
    })
  }

  hookDependants() {
    let fieldNames = this.workFlowFields.flat().map(obj => obj.key);
    let dropdownfieldsWithParent = fieldNames.filter(name => this.metafields[name].parent);
    dropdownfieldsWithParent.forEach(field => {
      let fieldDetails = this.metafields[field];
      let parent = fieldDetails.parent[0];
      if (this.deliveryDetailsForm.get(parent)) {
        this.deliveryDetailsForm.get(parent).valueChanges.subscribe((res: any) => {
          let mdmPayload = [{
            serviceKey: fieldDetails.serviceKey,
            dependsOn: [res]
          }];
          this.deliveryService.getMDMdata(mdmPayload).subscribe(res => {
            this.metafields[field].options = res[fieldDetails.serviceKey];
          })
        })
      } else {
        let generalDetails = {};
        if (!this.isEdit) {
          generalDetails = _.get(this.selected, `selected.createTrade_PNG`, {});
        } else {
          generalDetails = _.get(this.selected, `selected.workflow_updateGeneralDetails_PNG`, {});
        }
        let parent = fieldDetails['parent'];
        if (parent) {
          let _mdmPayload = [];
          _mdmPayload.push(
            {
              'serviceKey': fieldDetails.serviceKey,
              'dependsOn': [generalDetails[parent]]
            }
          );
          if (_mdmPayload.length > 0) {
            this.deliveryService.getMDMdata(_mdmPayload).subscribe(res => {
              this.metafields[field].options = res[fieldDetails.serviceKey];
            })
          }
        }
      }
    });
  }

  fetchCollectionData() {
    this.deliveryService.getCollectionData().subscribe((res: any) => {
      res.data.push({value: '', key: null})
      this.metafields['facilityLocation'].options = res.data;
    })
  }

  workFlow(workFlowTask) {
    if (this.deliveryDetailsForm.valid) {
      this.enterWorkflow = true;
      if (!(workFlowTask && workFlowTask['type'] === 'submit')) {
        return this.appService.workFlow(this.appName, this.appMeta.sys__UUID, workFlowTask.outcomes, false);
      }
      if (!this.isEdit && this.tableValidation()) {
        this.createContract();
      } else if (this.tableValidation()) {
        this.updateContract();
      }
    } else {
      console.log(this.deliveryDetailsForm)
      this.finalValidation = true;
      this.errorMsg = "Please fill all the required fields appropriately."
      this.showWarning = true;
    }
  }

  tableValidation() {
    let blockDetails: any = this.deliveryService.getBlockDetails();
    if (blockDetails.length > 0) {
      if (this.deliveryDetailsForm.get('deliveryType').value === 'Shape') {
        let invalid = this.shapeTable.validateShape();
        if (invalid) {
          console.log('shape table is invalid');
          return false;
        } else {
          console.log('shape table in valid');
          return true;
        }
      } else {
        let invalid = this.blockTable.validateBlock();
        if (invalid) {
          console.log('block table is invalid');
          return false;
        } else {
          console.log('block table in valid');
          return true;
        }
      }
    } else {
      this.showWarning = true;
      this.errorMsg = 'add atlest 1 block/shape data';
    }
  }

  getGeneralDetails(flowName) {
    let page1_generalDetails = {}
    if (_.has(this.selected, `selected.${flowName}`)) {
      page1_generalDetails = _.get(this.selected, `selected.${flowName}`,{});
    } else if (_.has(this.selected, `selected.powerlisting`)) {
      page1_generalDetails = _.get(this.selected, `selected.powerlisting`,{})
    } else {
      console.log('nothing found');
      let contractNo = this.route.snapshot.queryParams.powerContractRefNo
      page1_generalDetails = { powerContractRefNo: contractNo }
    }
    let page2_generalDetails = { ...this.deliveryDetailsForm.getRawValue(), ...this.displayValues };
    let generalDetails = { ...page1_generalDetails, ...page2_generalDetails };
    console.log(generalDetails);
    this.deliveryService.updateGeneralDetails(generalDetails);
    return generalDetails;
  }

  createContract() {
    let generalDetails = this.getGeneralDetails('createTrade_PNG');
    let { powerContractRefNo } = generalDetails;
    let blockDetails = this.deliveryService.getBlockDetails();
    let blocksWithContractRefNo = blockDetails.map(block => { block.powerContractRefNo = powerContractRefNo; return block });
    let blockDetailsWorkFlowTaskNew = {
      workflowTaskName: "itemDetails_PNG",
      task: "itemDetails_PNG",
      appName: this.appName,
      appId: this.appMeta.sys__UUID,
      output: { "itemDetails_PNG": blocksWithContractRefNo }
    };
    let deliveryDetailsWorkFlowTaskNew = {
      workflowTaskName: "workflow_updateGeneralDetails_PNG",
      task: "workflow_updateGeneralDetails_PNG",
      appName: this.appName,
      appId: this.appMeta.sys__UUID,
      output: { "workflow_updateGeneralDetails_PNG": generalDetails },
      id: generalDetails._id
    };
    this.checkDeliveryTypeAndSave(generalDetails, blocksWithContractRefNo, blockDetailsWorkFlowTaskNew, deliveryDetailsWorkFlowTaskNew);
  }

  updateContract() {
    let generalDetails = this.getGeneralDetails('workflow_updateGeneralDetails_PNG');
    let blockDetails = this.deliveryService.getBlockDetails();
    let { powerContractRefNo } = generalDetails;
    let blockData = blockDetails.filter(block => {
      if (!block.powerContractRefNo) {
        block.powerContractRefNo = powerContractRefNo;
      }
      if (block._id && block.powerItemRefNo) {
        block.id = block._id;
        delete block._id;
      }
      return block;
    });
    let blockDetailsWorkFlowTaskNew = {
      workflowTaskName: "update_itemDetails",
      task: "update_itemDetails",
      appName: this.appName,
      appId: this.appMeta.sys__UUID,
      output: { "update_itemDetails": blockData }
    };
    let deliveryDetailsWorkFlowTaskNew = {
      workflowTaskName: "workflow_updateGeneralDetails_PNG",
      task: "workflow_updateGeneralDetails_PNG",
      appName: this.appName,
      appId: this.appMeta.sys__UUID,
      output: { "workflow_updateGeneralDetails_PNG": generalDetails },
      id: generalDetails._id
    };
    this.checkDeliveryTypeAndSave(generalDetails, blockData, blockDetailsWorkFlowTaskNew, deliveryDetailsWorkFlowTaskNew);
  }

  checkDeliveryTypeAndSave(generalDetails, blocksWithContractRefNo, tableWorkflow, generalDataWorkflow) {
    if (generalDetails['deliveryType'] === 'Block') {
      let blockDetailsString = JSON.stringify(blocksWithContractRefNo);
      let blockFileSaveWorkFlowTask = {
        workflowTaskName: "block_file",
        task: "block_file",
        appName: this.appName,
        appId: this.appMeta.sys__UUID,
        payLoadData: "",
        output: { "block_file": { "blockDetails": blockDetailsString } }
      };
      this.apiCalled = true;
      this.workflowApiCall(blockFileSaveWorkFlowTask)
        .pipe(concatMap((res: any) => {
          let blockWithFileDetails = blocksWithContractRefNo.map(block => { block['fileDetails'] = res.data[block['blockNo']]; return block });
          let workflowName = Object.keys(tableWorkflow.output);
          tableWorkflow.output[workflowName[0]] = blockWithFileDetails;
          //this.mockBlock()
          //this.workflowApiCall(tableWorkflow)
          return forkJoin(this.workflowApiCall(tableWorkflow),this.workflowApiCall(generalDataWorkflow))
        })
        )
        .subscribe((res: any) => {
          let action = `created`;
          if(this.isEdit){
            action = `updated`;
          }
          this.popupMsgExit(`power contract with Reference Number ${res[1].data['powerContractRefNo']} has been ${action}`);
        }, error => {
          this.apiCalled = false;
          this.showWarning = true;
          this.errorMsg = 'Failed to create Block Contract';
        });
    } else {
      this.saveTableDataAndGeneralDetails(tableWorkflow, generalDataWorkflow);
    }
  }

  saveTableDataAndGeneralDetails(tableWorkflow, generalDataWorkflow) {
    forkJoin(this.workflowApiCall(tableWorkflow), this.workflowApiCall(generalDataWorkflow))
      .subscribe((res: any) => {
        this.popupMsgExit(`power contract with Reference Number - ${res[1].data.powerContractRefNo} has been updated`);
      }, error => {
        this.apiCalled = false;
        this.showWarning = true;
        this.errorMsg = 'Failed to create Shape Contract';
      });
  }

  popupMsgExit(msg) {
    this.contractSavePopup.open(msg);
    this.router.navigate([`app/${this.appName}/powerlisting`]);
  }

  redirectToListing() {
    //window.location.href = '/connect/trm910/app/power/powerlisting'
  }

  workflowApiCall(workFlowData) {
    let httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this.http.post(`/workflow`, workFlowData, httpOptions)
  }

  mockBlock(){
    return of({
      "data": {
        "1": {
          "quantity": {
            "bucketDir": "trmga/9c86d836-36e7-41f1-bb6f-71efd7df43aa/powerDocs",
            "description": "Block file",
            "fileContentType": null,
            "fileId": null,
            "fileName": "block_1_4781890_.csv",
            "id": "5f59a97264f547000140c1ca.csv",
            "otherAttributes": null,
            "refObject": "power",
            "refObjectId": "9c86d836-36e7-41f1-bb6f-71efd7df43aa",
            "s3Tags": null,
            "size": 116,
            "tags": null,
            "uploadedBy": "QA SD",
            "uploadedDate": null,
            "validator": {}
          }
        }
      },
      "navigateURL": "block_file",
      "name": "block_file",
      "message": "Profile got created successfully",
      "cookies": [
        {
          "name": "_ga",
          "value": "GA1.2.1291524295.1592828795",
          "version": 0,
          "comment": null,
          "domain": null,
          "maxAge": -1,
          "path": null,
          "secure": false,
          "httpOnly": false
        },
        {
          "name": "Test",
          "value": "Test",
          "version": 0,
          "comment": null,
          "domain": null,
          "maxAge": -1,
          "path": null,
          "secure": false,
          "httpOnly": false
        },
        {
          "name": "CAC_SSO_COOKIE",
          "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsicmVzdF9hcGkiXSwidXNlcl9uYW1lIjoibWFkaHVAZWthcGx1cy5jb20iLCJzY29wZSI6WyJ0cnVzdCIsInJlYWQiLCJ3cml0ZSJdLCJleHAiOjE1OTkxNTQ1ODQsImF1dGhvcml0aWVzIjpbIjE3Mi4xNy4wLjEiXSwianRpIjoiYzk2Y2ZlNDMtZGQ1Yi00NmQ2LWE1NDAtMjZiOTVlZTg5ZjAxIiwiY2xpZW50X2lkIjoiNzRkN2UxZTQtNzM4ZS0zNzZjLWE0N2QtMTZhZTczNjljYjgxIiwidGlkIjoiN2YyNGQyNDAtNTIxZC0zOTA3LTljOTMtYWYzOTE3MjE1ZWY3In0.ZT7DQbu1WaGcuWT9UM7Rt5z9BTtaZHZmgmjlH71qL5Y",
          "version": 0,
          "comment": null,
          "domain": null,
          "maxAge": -1,
          "path": null,
          "secure": false,
          "httpOnly": false
        }
      ]
    })
  }

  initializePricingData() {
    this.contractData = this.deliveryPricingService.contractData

    this.priceUnitOptions = this.deliveryPricingService.priceUnitOptions

    this.deliveryPricingService.formulaDetails.subscribe((res: any) => {
      if (_.get(this.deliveryPricingService.getPricingInvocationSource(), 'name', '') === 'valuationFormula') {
        this.pricingFormulaName = res[0].formulaName;
        console.log(this.pricingFormulaName);
        this.deliveryDetailsForm.get('valuationFormulaId').setValue(res[0]._id);
      }
    });
  }

  setPricingInvocation(val) {
    if (this.pricingFormulaName) {
      this.contractData.itemDetails[0].pricing.pricingFormulaId = this.deliveryDetailsForm.get('valuationFormulaId').value;
    }
    this.deliveryPricingService.setPricingInvocationSource({ name: val });
  }

  onLoadSetValuationFormulaDetails(id) {
    this.deliveryService.getFormulaDetails(id).subscribe((res: any) => {
      console.log(res);
      this.pricingFormulaName = res[0].formulaName;
    })
  }

  getSelectedTxt(event, field, type = 'select') {
    let text
    if (type === 'select') {
      text = event.target.options[event.target.options.selectedIndex].text;
    }
    this.displayValues[field + "DisplayName"] = text;
  }

  closeAlert() {
    this.showWarning = false;
  }

  handleAlert(showAlert){
    if(showAlert){
      setTimeout(() => this.showWarning = false, 3000);
    }
    return showAlert;
  }

}
