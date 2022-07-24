import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';

import { ThemeModule } from '@eka-framework/theme';
import { LayoutModule } from '@eka-framework/layout';
import { GenericCRUDModule } from '@eka-framework/modules/generic-crud/generic-crud.module';
import { CreateMenuModule } from '@eka-framework/modules/custom-components/create-menu/create-menu.module';

import { TableModule } from 'primeng/table';
import { DropdownModule, MultiSelectModule } from 'primeng/primeng';
import { CalendarModule } from 'primeng/calendar';

import { NgxJsonViewerModule } from 'ngx-json-viewer';

import { PricingModule } from '@app/views/Pricing/pricing-app/pricing.module';
import { FormulaListModule } from '@app/views/Pricing/pricing-app/formula-list/formula-list.module';
import { FormulaFormModule } from '@app/views/Pricing/pricing-app/formula-form/formula-form.module';

import { DeliveryDetails } from './deliveryDetails.power.component';
import { DeliveryDetailsRoutingModule } from './deliveryDetails.power.routing.module';
import { PricingPopupComponent } from './pricing-popup/pricing-popup.component';
import { FormulaDetailsPopupComponent } from './formula-details-popup/formula-details-popup.component';
import { BlockDetailsComponent } from './block-details/block-details.component';
import { ShapeDetailsComponent } from './shape-details/shape-details.component';
import { DaysPickerComponent } from './block-details/days-picker/days-picker.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { OverlayPanelModule } from 'primeng/overlaypanel';
import { TabViewModule } from 'primeng/tabview';
import { ConfirmPopupComponent } from './confirm-popup/confirm-popup.component';
import { ShapeConfigPopupComponent } from './shape-details/shape-config/shape-config-popup/shape-config-popup.component';
import { ShapeConfigTableComponent } from './shape-details/shape-config/shape-config-table/shape-config-table.component';
import { ShapeConfigCellEditComponent } from './shape-details/shape-config/shape-config-table/shape-config-cell-edit/shape-config-cell-edit.component';

@NgModule({
  imports: [
    CommonModule,
    NgxJsonViewerModule,
    ThemeModule,
    LayoutModule,
    FormsModule,
    ReactiveFormsModule,
    TableModule,
    CalendarModule,
    DropdownModule,
    MultiSelectModule,
    TabViewModule,
    OverlayPanelModule,
    GenericCRUDModule,
    CreateMenuModule,
    FormulaListModule,
    FormulaFormModule,
    PricingModule,
    DeliveryDetailsRoutingModule,
    NgbModule
  ],
  declarations: [DeliveryDetails, BlockDetailsComponent, ShapeDetailsComponent, PricingPopupComponent, FormulaDetailsPopupComponent, DaysPickerComponent, ShapeConfigPopupComponent, ShapeConfigTableComponent, ShapeConfigCellEditComponent, ConfirmPopupComponent]
})
export class DeliveryDetailsPNG { }
