import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import {AuthModule} from './auth/auth.module';
import {provideNativeDateAdapter} from '@angular/material/core';
import {provideHttpClient} from '@angular/common/http';
import {SharedModule} from "./shared/shared.module";
import {LayoutModule} from "./layout/layout.module";
import { ArtistModule } from './artist/artist.module';
import {MusicContentModule} from './music-content/music-content.module';
import {MediaModule} from './media/media.module';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    SharedModule,
    LayoutModule,
    AuthModule,
    MediaModule,
    ArtistModule,
    MusicContentModule,
  ],
  providers: [
    provideNativeDateAdapter(),
    provideHttpClient()
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
