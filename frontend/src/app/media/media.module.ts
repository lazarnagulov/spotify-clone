import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SongDetailsComponent } from './song-details/song-details.component';
import {MediaCardComponent} from './media-card/media-card.component';
import {MaterialModule} from '../infrastructure/material/material.module';
import {RouterLink} from '@angular/router';
import {AlbumDetailsComponent} from './album-details/album-details.component';



@NgModule({
  declarations: [
    SongDetailsComponent,
    AlbumDetailsComponent,
    MediaCardComponent
  ],
  exports: [
    MediaCardComponent
  ],
  imports: [
    CommonModule,
    MaterialModule,
    RouterLink,
  ]
})
export class MediaModule { }
