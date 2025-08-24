import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ArtistDetailsComponent } from './artist-details/artist-details.component';
import { AlbumDetailsComponent } from './album-details/album-details.component';
import { SongDetailsComponent } from './song-details/song-details.component';
import {MediaCardComponent} from './media-card/media-card.component';
import {MaterialModule} from '../infrastructure/material/material.module';
import {RouterLink} from '@angular/router';



@NgModule({
  declarations: [
    ArtistDetailsComponent,
    AlbumDetailsComponent,
    SongDetailsComponent,
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
