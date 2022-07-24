import { Component, OnInit, Input, SimpleChanges, Output, EventEmitter, ViewEncapsulation } from '@angular/core';
import { NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import * as xlsx from 'xlsx';
import * as FileSaver from 'file-saver';
import { DeliveryDetailsService } from '../../../delivery-details.service';
import { BehaviorSubject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';
import { FormBuilder } from '@angular/forms';
import { OverlayPanel } from 'primeng/primeng';
import * as _ from 'lodash';

@Component({
  selector: 'shape-config-table',
  templateUrl: './shape-config-table.component.html',
  styleUrls: ['./shape-config-table.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class ShapeConfigTableComponent implements OnInit {

  @Input() shapeDetails
  @Input() shapeIndex
  @Input() priceType
  @Input() tabValue = 'contracted'
  closeResult: string;
  columns
  shapeDefinitionColumns
  shapeDefinition
  totalRecords
  loading = true;
  scrollRefRowIndex
  updateEvent = new BehaviorSubject(null);
  displayValForm
  dropdownOptions = ["All", "Quantity", "Price"]
  dropdownValue = "Quantity"
  fileUploadForm = {}
  currentCellData = {
    rowIndex: '',
    colIndex: '',
    colName: '',
    nextColName: '',
    rowName: '',
    nextRowName: '',
    cellValue: '',
    rowData: ''
  };
  @Output() shapeConfig = new EventEmitter<object>();
  shapeFileDetails : any = { 
    'contracted' : {},
    'nominated' : {},
    'actuals' : {}
  }
  updatedFiles : any = { }
  fileNotFoundWarning = false;
  errorMsg = ""

  constructor(private fb: FormBuilder, private modalService: NgbModal, private deliveryService: DeliveryDetailsService) { }

  ngOnInit() {
    this.displayValForm = this.fb.group({ 'displayVal': ["Quantity"], fileDetails: [''] });
    this.displayValForm.get('displayVal').valueChanges.subscribe((res:any) => {
      this.dropdownValue = res;
      this.shapeDefinition = []
      this.shapeDefinitionColumns = []
      this.updateShapeDataFromFile(this.getFileName());
    })
    this.updateEvent.pipe(debounceTime(1000))
      .subscribe((res: any) => this.updateShapeConfig(res));
    this.deliveryService.shapeFilesSubject.subscribe(res=>{
      console.log('this is the shape file details from shapeFilesSubject...');
      console.log(res);
      this.setshapeFileDetails(res);
    })
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.priceType) {
      this.priceType = changes.priceType.currentValue;
      if(this.priceType === 'Fixed'){
        this.dropdownOptions = ["All", "Quantity", "Price"]
      }else{
        this.dropdownOptions = ["Quantity"]
      }
    }
    if (changes.tabValue) {
      this.tabValue = changes.tabValue.currentValue;
      if(_.has(this.shapeDetails.shape, [this.tabValue, this.dropdownValue, 'fileName'])){
        this.updateShapeDataFromFile(this.shapeDetails.shape[this.tabValue][this.dropdownValue].fileName)
      }
    }
  }

  setshapeFileDetails(shape){
    if(shape !== 'Configure'){
      this.shapeFileDetails = shape;
      if(_.has(shape, [this.tabValue, this.dropdownValue, 'fileName'])){
        this.updateShapeDataFromFile(shape.contracted.Quantity.fileName)
      }
      this.totalRecords = 200;
    }
  }

  requestDataFile(msg){
    this.errorMsg = msg;
    this.fileNotFoundWarning = true;
  }

  closeAlert(alert){
    this.fileNotFoundWarning = false;
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

  exportExcel() {
    const worksheet = xlsx.utils.json_to_sheet(this.shapeDefinition);
    const workbook = { Sheets: { 'data': worksheet }, SheetNames: ['data'] };
    const excelBuffer: any = xlsx.write(workbook, { bookType: 'xlsx', type: 'array' });
    this.saveAsExcelFile(excelBuffer, "primengTable");
  }

  saveAsExcelFile(buffer: any, fileName: string): void {
    let EXCEL_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8';
    let EXCEL_EXTENSION = '.xlsx';
    const data: Blob = new Blob([buffer], {
      type: EXCEL_TYPE
    });
    FileSaver.saveAs(data, fileName + '_export_' + new Date().getTime() + EXCEL_EXTENSION);
  }

  getShapeConfigColumns() {
    this.loading = true;
    let fileName = this.getFileName();
    this.deliveryService.getShapeConfigColumns(fileName).subscribe((res: any) => {
      console.log('---columns---');
      console.log(res);
      this.shapeDefinitionColumns = res.data.columns;
      this.loading = false;
      this.onScroll({ 'first': 0 });
    })
  }

  onScroll(event) {
    this.scrollRefRowIndex = event.first;
    let fileName = this.getFileName();
    if(fileName){
      this.loading = true;
      let shape_data = { 
        "startingRow": event.first, 
        "fileName": fileName,
        "startDate": this.shapeDetails.startDate,
        "endDate": this.shapeDetails.endDate
      }
      this.deliveryService.getShapeConfigData(shape_data).subscribe((res: any) => {
        this.shapeDefinition = JSON.parse(res.data.rows);
        console.log('---rows---');
        console.log(this.shapeDefinition);
        this.loading = false;
      })
    }
  }

  shapeConfigChanged(data) {
    console.log("---shapeConfigChanged---");
    let rowIndex = data.rowIndex + this.scrollRefRowIndex;
    let colName = this.shapeDefinitionColumns[data.colIndex];
    let body = {
      'rowIndex': rowIndex,
      'colIndex': data.colIndex,
      'attribute': data.attribute,
    }
    if (data.attribute === 'All') {
      let value = data.Quantity + '  |  ' + data.Price;
      this.shapeDefinition[rowIndex][colName] = value;
      body['Quantity'] = data.Quantity;
      body['Price'] = data.Price;
      body['Quantity_file'] = this.shapeFileDetails[this.tabValue].Quantity.fileName;
      body['Price_file'] = this.shapeFileDetails[this.tabValue].Price.fileName;
      this.updatedFiles = this.shapeFileDetails;
    } else {
      body['value'] = data.value;
      body['fileName'] = this.getFileName();
      this.shapeDefinition[rowIndex][colName] = data.value;
      this.updatedFiles[this.tabValue] = {};
      this.updatedFiles[this.tabValue][data.attribute] = this.shapeFileDetails[this.tabValue][data.attribute];
    }
    console.log(body);
    this.updateEvent.next(body);
  }

  updateShapeConfig(body) {
    if (body) {
      this.deliveryService.updateShapeConfigData(body)
        .subscribe(res => {
          console.log('---shape config updated---');
          console.log(res);
        })
    }
  }

  getFileName(){
    let defaultPath =  this.shapeFileDetails[this.tabValue][this.dropdownValue]
    if(this.dropdownValue === 'All'){
      return 'All';
    }else if(defaultPath){
      return defaultPath.fileName;
    }else{
      this.createInitialShapeFile();
    }
  }

  fileChange(event) {
    this.loading = true;
    let formData = new FormData();
    let file: File = event.target.files[0];
    formData.set('file', file);
    formData.set('refObject', 'file_object')
    formData.set('refObjectId', '9c86d836-36e7-41f1-bb6f-71efd7df43aa')
    formData.set('description', 'Power App, Shape Config file')

    let contractDetails : any = this.deliveryService.getGeneralDetails();
    let { powerContractRefNo } = contractDetails;
    let otherAttributes = JSON.stringify({ powerContractRefNo, 'shapeType': '' ,'shapeAttribute' : this.dropdownOptions});
    formData.set('otherAttributes', otherAttributes);
   
    this.deliveryService.uploadFileToFileSysFromUI(formData).subscribe((res:any) => {
      this.shapeFileDetails[this.tabValue][this.dropdownValue] = res;
      this.shapeConfig.emit({shape: this.shapeFileDetails, index: this.shapeIndex});
      this.downloadFile(res);
    });
  }

  setCurrentCellData($event, overlaypanel: OverlayPanel, rowIndex, colIndex, colName, cellValue, rowData) {
    let firstColName = this.shapeDefinitionColumns[0];
    let rowName = this.shapeDefinition[rowIndex][firstColName];
    let nextRowName = this.shapeDefinition[rowIndex + 1][firstColName];
    let nextColName = this.shapeDefinitionColumns[colIndex + 1];
    let currentCellData = {
      rowIndex,
      colIndex,
      colName,
      nextColName,
      rowName,
      nextRowName,
      cellValue,
      rowData,
      overlaypanel
    }
    this.currentCellData = currentCellData;
    console.log('---cell editing data---');
    console.log(this.currentCellData);
    console.log(overlaypanel);
    overlaypanel.toggle($event);
  }

  downloadFile(fileDetails) {
    let fileData = { ...fileDetails, ...this.shapeDetails }
    fileData['tab'] = this.tabValue;
    fileData['dropdown'] = this.dropdownValue;
    fileData['timeFrequency'] = this.shapeDetails['timeFrequency'];
    let data = {
      "task": "shape_file_download",
      "workflowTaskName": "shape_file_download",
      "appName": "power",
      "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      "payLoadData": "",
      "output": {
        "shape_file_download": fileData
      }
    }
    this.deliveryService.downloadFileFromS3(data).subscribe((res:any) => {
      console.log("---file downloaded---");
      console.log(res);
      res.data["storageType"] = "fileSys";
      this.shapeFileDetails[this.tabValue][this.dropdownValue]['fileName'] = res.data.fileName;
      this.updateShapeDataFromFile(res.data.fileName);
      this.shapeConfig.emit({shape: this.shapeFileDetails, index: this.shapeIndex});
    })
  }

  updateShapeDataFromFile(val) {
    if(val){
      let data = {
        "task": "shape_file",
        "workflowTaskName": "shape_file",
        "appName": "power",
        "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
        "output": { "shape_file": {}  },
        "payLoadData": ""
      }
      if(val === 'All'){
        data.output.shape_file["dropdown"] = 'All';  
      }else{
        data.output.shape_file["dropdown"] = this.dropdownValue;
      }
      data.output.shape_file['fileDetails'] = this.shapeFileDetails[this.tabValue];
      this.deliveryService.shapeFileChange(data).subscribe(res => {
        console.log('---file changed---');
        console.log(res);
        this.getShapeConfigColumns();
      })
    }
  }

  saveShapeConfig(modal){
    this.loading = true;
    if(Object.keys(this.updatedFiles).length > 0){
      let data = {
        "task": "shape_file_updateToS3",
        "workflowTaskName": "shape_file_updateToS3",
        "appName": "power",
        "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
        "payLoadData": "",
        "output": {
          "shape_file_updateToS3": { "shape" : this.updatedFiles }
        }
      }
      this.deliveryService.updateFiletoS3FromBackend(data).subscribe((res:any)=>{
        // need to check with tabs
        this.shapeFileDetails = { ...this.shapeFileDetails, ...res.data }
        this.shapeConfig.emit({shape: this.shapeFileDetails, index: this.shapeIndex});
        this.loading = false;
        modal.close('Save click');
      })
    }else{
      this.loading = false;
      modal.close('Save click');
    }
  }

  createInitialShapeFile(){
    let data = {
      "task": "createInitialShapeFile",
      "workflowTaskName": "createInitialShapeFile",
      "appName": "power",
      "appId": "d7d05837-88a3-471e-a5f1-1c5fd6cec3e7",
      "output": { "createInitialShapeFile": this.shapeDetails  },
      "payLoadData": ""
    }
    this.deliveryService.shapeFileChange(data).subscribe((res:any) => {
      this.shapeFileDetails[this.tabValue][this.dropdownValue] = { "fileName" : res.data.initialFileName }
      this.updateShapeDataFromFile(res.data.initialFileName);
      this.shapeConfig.emit({shape: this.shapeFileDetails, index: this.shapeIndex});
    })
  }

}
