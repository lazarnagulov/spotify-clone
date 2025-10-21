import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../env/environment';
import {Song} from '../shared/model/media/song.model';

@Injectable({
  providedIn: 'root',
})
export class MediaService {
  constructor(private http: HttpClient) {}

  deleteSong(id: string): Observable<void> {
    return this.http.delete<void>(`${environment.apiHost}/songs/${id}`);
  }

  deleteAlbum(id: string): Observable<void> {
    return this.http.delete<void>(`${environment.apiHost}/albums/${id}`);
  }

  getOfflineUrl(id: string) {
    return this.http.get<any>(`${environment.apiHost}/songs/${id}/offline_url`);
  }

  getSong(id: string): Observable<Song> {
    return this.http.get<Song>(`${environment.apiHost}/songs/${id}`);
  }

  getTranscription(id: string): Observable<{ transcript: string | null }> {
    return this.http.get<{ transcript: string | null }>(
      `${environment.apiHost}/transcriptions/${id}`
    );
  }
}
