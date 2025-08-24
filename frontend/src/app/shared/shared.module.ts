import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MediaCardComponent } from './media-card/media-card.component';
import {MaterialModule} from '../infrastructure/material/material.module';



@NgModule({
  declarations: [
    MediaCardComponent
  ],
  exports: [
    MediaCardComponent
  ],
  imports: [
    CommonModule,
    MaterialModule
  ]
})
export class SharedModule { }
