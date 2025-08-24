import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MediaCardComponent } from './media-card/media-card.component';
import {MaterialModule} from '../infrastructure/material/material.module';
import {RouterLink} from "@angular/router";



@NgModule({
  declarations: [
    MediaCardComponent
  ],
  exports: [
    MediaCardComponent
  ],
    imports: [
        CommonModule,
        MaterialModule,
        RouterLink
    ]
})
export class SharedModule { }
