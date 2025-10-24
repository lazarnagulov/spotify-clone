import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Artist } from './model/create-artist.model';
import { Observable } from 'rxjs';
import { environment } from '../../env/environment';
import { UpdateArtistRequest } from './model/update-artist.model';

@Injectable({
  providedIn: 'root',
})
export class ArtistService {
  constructor(private httpClient: HttpClient) {}

  createArtist(artist: Artist): Observable<Artist> {
    return this.httpClient.post<Artist>(environment.apiHost + "/artists",artist);}

  getArtists(): Observable<{ artists: Artist[] }> {
    return this.httpClient.get<{ artists: Artist[] }>(environment.apiHost + '/artists');
  }

  getDetails(id: string): Observable<Artist> {
    return this.httpClient.get<Artist>(`${environment.apiHost}/artists/${id}`);
  }

  deleteArtist(id: string): Observable<void> {
    return this.httpClient.delete<void>(`${environment.apiHost}/artists/${id}`);
  }

  updateArtist(id: string, request: UpdateArtistRequest): Observable<void> {
    return this.httpClient.put<void>(`${environment.apiHost}/artists/${id}`, request);
  }
}
