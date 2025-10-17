import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {RegisterComponent} from './auth/register/register.component';
import {LoginComponent} from './auth/login/login.component';
import {HomeComponent} from './layout/home/home.component';
import {ArtistDetailsComponent} from './artist/artist-details/artist-details.component';
import {SongDetailsComponent} from './media/song-details/song-details.component';
import {AlbumDetailsComponent} from './media/album-details/album-details.component';
import { ArtistCreationComponent } from './artist/artist-creation/artist-creation.component';
import {CreateSongComponent} from './music-content/create-song/create-song.component';
import {CreateAlbumComponent} from './music-content/create-album/create-album.component';
import {AuthGuard} from './auth/auth.guard';
import {SubscriptionsComponent} from './subscription/subscriptions/subscriptions.component';

const routes: Routes = [
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent },
  {
    path: 'artist-creation',
    component: ArtistCreationComponent,
    canActivate: [AuthGuard],
    data: { roles: ['admin'] }
  },
  {
    path: 'song-creation',
    component: CreateSongComponent,
    canActivate: [AuthGuard],
    data: { roles: ['admin'] }
  },
  {
    path: 'album-creation',
    component: CreateAlbumComponent,
    canActivate: [AuthGuard],
    data: { roles: ['admin'] }
  },
  {
    path: 'subscriptions',
    component: SubscriptionsComponent,
    canActivate: [AuthGuard],
    data: { roles: ['admin', 'user'] }
  },
  { path: 'home', component: HomeComponent },
  { path: 'artist/:id', component: ArtistDetailsComponent },
  { path: 'song/:id', component: SongDetailsComponent },
  { path: 'album/:id', component: AlbumDetailsComponent },
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: '**', redirectTo: '/home', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
