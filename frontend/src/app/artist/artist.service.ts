import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Artist } from './model/create-artist.model';
import { Observable } from 'rxjs';
import { environment } from '../../env/environment';

@Injectable({
  providedIn: 'root'
})
export class ArtistService {

  constructor(
    private httpClient: HttpClient
  ) { }

  createArtist(artist: Artist): Observable<Artist> {
    return this.httpClient.post<Artist>(environment.apiHost + "/artists", artist);
  }
}
