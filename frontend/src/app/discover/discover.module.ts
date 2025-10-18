import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DiscoverComponent } from './discover/discover.component';
import { MediaModule } from '../media/media.module';
import { MaterialModule } from '../infrastructure/material/material.module';



@NgModule({
  declarations: [
    DiscoverComponent
  ],
  imports: [
    CommonModule,
    MaterialModule,
    MediaModule
  ]
})
export class DiscoverModule { }
