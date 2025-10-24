import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CreateSongComponent } from './create-song/create-song.component';
import {MaterialModule} from '../infrastructure/material/material.module';
import {ReactiveFormsModule} from '@angular/forms';
import { CreateAlbumComponent } from './create-album/create-album.component';
import { EditSongComponent } from './edit-song/edit-song.component';
import { EditAlbumComponent } from './edit-album/edit-album.component';



@NgModule({
  declarations: [
    CreateSongComponent,
    CreateAlbumComponent,
    EditSongComponent,
    EditAlbumComponent
  ],
  imports: [
    CommonModule,
    MaterialModule,
    ReactiveFormsModule,
  ]
})
export class MusicContentModule { }
