import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {MaterialModule} from '../infrastructure/material/material.module';
import {RouterLink} from "@angular/router";



@NgModule({
  declarations: [
  ],
  exports: [
  ],
    imports: [
        CommonModule,
        MaterialModule,
        RouterLink
    ]
})
export class SharedModule { }
