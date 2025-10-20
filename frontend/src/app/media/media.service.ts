import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../env/environment';

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

  getTranscription(id: string): Observable<{ transcript: string | null }> {
    return this.http.get<{ transcript: string | null }>(
      `${environment.apiHost}/transcriptions/${id}`
    );
  }
}
