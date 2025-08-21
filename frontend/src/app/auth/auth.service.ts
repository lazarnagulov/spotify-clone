import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../env/environment';
import {RegisterRequest} from './model/register-request.model';
import {RegisterResponse} from './model/register-response.model';
import {ConfirmRequest} from './model/confirm-request.model';
import {ConfirmResponse} from './model/confirm-response.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(private httpClient: HttpClient) { }

  register(request: RegisterRequest): Observable<RegisterResponse> {
    console.log(request);
    return this.httpClient.post<RegisterResponse>(`${environment.apiHost}/registration`, request);
  }

  confirm(request: ConfirmRequest): Observable<ConfirmResponse> {
    return this.httpClient.post<ConfirmResponse>(`${environment.apiHost}/confirmation`, request);
  }

}
