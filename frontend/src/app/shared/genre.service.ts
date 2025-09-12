import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import {environment} from '../../env/environment';

@Injectable({
  providedIn: 'root'
})
export class GenreService {

  constructor(
    private httpClient: HttpClient
  ) { }

  getGenres(): Observable<string[]> {
      return this.httpClient.get<{ genres: string[] }>(`${environment.apiHost}/genres`)
        .pipe(map(response => response.genres || []));
  }
}
