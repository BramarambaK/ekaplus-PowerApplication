import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { APP_BASE_HREF, Location } from '@angular/common';

import { EkaFrameworkModule } from '@eka-framework/framework.module';
import { ApplicationModule } from './views/application/application.module';
// import { TabsModule } from 'ngx-bootstrap/tabs';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { LoadingBarHttpClientModule } from '@ngx-loading-bar/http-client';
import { NgxSpinnerModule } from 'ngx-spinner';

import { StoreModule } from '@ngrx/store';
import { storeDataReducer } from './views/application/dynamicFormBuilder/ng-rx/reducer';

import { ToastrModule } from 'ngx-toastr';

import { ContractsModule } from './views/Contracts-Physicals/physicals-app/contracts.module';
import { DeliveryDetailsPNG } from './views/PowerApplication/power-app/deliveryDetails.power.module';
import { PricingModule } from './views/Pricing/pricing-app/pricing.module';
import { ContractApprovalComponent } from'./views/Contracts-Physicals/physicals-app/Contracts/contract-approval/contract-approval.component';


@NgModule({
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    ToastrModule.forRoot({
      timeOut: 10000,
      positionClass: 'toast-top-center',
      preventDuplicates: true
    }),
    //FormsModule,
    NgxSpinnerModule,
    ReactiveFormsModule,
    HttpClientModule,
    LoadingBarHttpClientModule,
    ContractsModule,
    DeliveryDetailsPNG,
    PricingModule,
    ApplicationModule,
    StoreModule.forRoot({ storeData: storeDataReducer }),
    EkaFrameworkModule,
    AppRoutingModule // must be imported as the last module as it contains the fallback route
  ],
  declarations: [AppComponent, ContractApprovalComponent],
  providers: [
    {
      provide: APP_BASE_HREF,
      useValue: '/connect' + window['_app_base'] || '/connect/'
    }
  ],
  bootstrap: [AppComponent],
  entryComponents: [ContractApprovalComponent]
})
export class AppModule {}
