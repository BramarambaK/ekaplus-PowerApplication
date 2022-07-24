import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { CtrmLayoutComponent, ConfigService } from '@eka-framework/layout';
import { DeliveryDetails } from './deliveryDetails.power.component';
import { AuthenticationGuard } from '@eka-framework/core';

const routes: Routes = [
  {
    path: 'app',
    component: CtrmLayoutComponent,
    resolve: { data: ConfigService },
    canActivate: [AuthenticationGuard],
    data: {
      title: 'Application'
    },
    children: [
      {
        path: ':app/:workflow/deliveryDetails_PNG',
        component: DeliveryDetails,
        data: {
          title: 'Apps'
        }
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DeliveryDetailsRoutingModule { }
