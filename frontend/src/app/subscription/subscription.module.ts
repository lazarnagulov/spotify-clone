import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {MaterialModule} from '../infrastructure/material/material.module';
import {SubscriptionsComponent} from './subscriptions/subscriptions.component';



@NgModule({
  declarations: [
    SubscriptionsComponent
  ],
  imports: [
    CommonModule,
    MaterialModule
  ]
})
export class SubscriptionModule { }
