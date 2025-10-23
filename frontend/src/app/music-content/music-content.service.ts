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

  updateSong(id: string, body: any): Observable<{ coverUploadPresignedUrl?: string; audioUploadPresignedUrl?: string }> {
    return this.http.put<{ coverUploadPresignedUrl?: string; audioUploadPresignedUrl?: string }>(
      `${environment.apiHost}/songs/${id}`,
      body
    );
  }
}
