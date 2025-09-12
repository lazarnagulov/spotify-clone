import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../infrastructure/material/material.module';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';

@NgModule({
  declarations: [
    ArtistCreationComponent,
  ],
  exports: [
    ArtistCreationComponent,
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MaterialModule,
  ]
})
export class ArtistModule { }
