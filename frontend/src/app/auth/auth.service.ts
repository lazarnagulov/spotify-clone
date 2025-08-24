import { Injectable } from '@angular/core';
import {catchError, Observable, throwError} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../env/environment';
import {RegisterRequest} from './model/register-request.model';
import {RegisterResponse} from './model/register-response.model';
import {ConfirmRequest} from './model/confirm-request.model';
import {ConfirmResponse} from './model/confirm-response.model';
import {ErrorHandlerService} from "../shared/error-handler.service";
import {LoginRequest} from './model/login-request.model';
import {LoginResponse} from './model/login-response.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(
      private httpClient: HttpClient,
      private errorHandler: ErrorHandlerService
) { }

  register(request: RegisterRequest): Observable<RegisterResponse> {
    return this.httpClient.post<RegisterResponse>(`${environment.apiHost}/registration`, request).pipe(
        catchError(err => throwError(() => this.errorHandler.handleError(err)))
    );
  }

  confirm(request: ConfirmRequest): Observable<ConfirmResponse> {
    return this.httpClient.post<ConfirmResponse>(`${environment.apiHost}/confirmation`, request).pipe(
        catchError(err => throwError(() => this.errorHandler.handleError(err)))
    );
  }

  login(request: LoginRequest): Observable<LoginResponse> {
    return this.httpClient.post<LoginResponse>(`${environment.apiHost}/login`, request).pipe(
        catchError(err => throwError(() => this.errorHandler.handleError(err)))
    );
  }

}
