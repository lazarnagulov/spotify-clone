import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../env/environment';
import { DiscoverResponse } from './model/discover-response.model';

@Injectable({
  providedIn: 'root'
})
export class DiscoverService {

  constructor(private http: HttpClient) { }

  getGenreData(genre: string): Observable<DiscoverResponse> {
    return this.http.get<DiscoverResponse>(environment.apiHost + "/discover/" + genre);
  }
}
