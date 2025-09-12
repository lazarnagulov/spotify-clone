import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../infrastructure/material/material.module';
import { ArtistCreationComponent } from './artist-creation/artist-creation.component';
import {ArtistDetailsComponent} from './artist-details/artist-details.component';
import {MediaModule} from '../media/media.module';

@NgModule({
  declarations: [
    ArtistDetailsComponent,
    ArtistCreationComponent,
  ],
  exports: [
    ArtistDetailsComponent,
    ArtistCreationComponent,
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MaterialModule,
    MediaModule,
  ]
})
export class ArtistModule { }
