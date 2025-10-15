import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CreateSongComponent } from './create-song/create-song.component';
import {MaterialModule} from '../infrastructure/material/material.module';
import {ReactiveFormsModule} from '@angular/forms';
import { CreateAlbumComponent } from './create-album/create-album.component';
import {MatList, MatListItem} from '@angular/material/list';



@NgModule({
  declarations: [
    CreateSongComponent,
    CreateAlbumComponent
  ],
  imports: [
    CommonModule,
    MaterialModule,
    ReactiveFormsModule,
  ]
})
export class MusicContentModule { }
