import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../env/environment';

@Injectable({
  providedIn: 'root'
})
export class MusicContentService {

  constructor(
    private http: HttpClient
  ) { }

  updateSong(id: string|undefined, body: any): Observable<{ coverUploadPresignedUrl?: string; audioUploadPresignedUrl?: string }> {
    return this.http.put<{ coverUploadPresignedUrl?: string; audioUploadPresignedUrl?: string }>(
      `${environment.apiHost}/songs/${id}`,
      body
    );
  }

  updateAlbum(id: string|undefined, body: any): Observable<{ presignedCoverUrl: string }> {
    return this.http.put<{ presignedCoverUrl: string }>(
      `${environment.apiHost}/albums/${id}`,
      body
    );
  }

  getAlbum(id: string): Observable<any> {
    return this.http.get<any>(`${environment.apiHost}/albums/${id}`);
  }
}
