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
import {getUserRoles} from './token-utils';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private accessToken: string | null = null;
  private idToken: string | null = null;
  private roles: string[] = [];

  constructor(
      private httpClient: HttpClient,
      private errorHandler: ErrorHandlerService
  ) { }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  getIdToken(): string | null {
    return this.idToken;
  }

  getRoles(): string[] {
    return this.roles;
  }

  hasRole(role: string): boolean {
    return this.roles.includes(role);
  }

  isLoggedId(): boolean {
    return this.accessToken !== null;
  }

  setTokens(tokens: LoginResponse): void {
    this.accessToken = tokens.AccessToken;
    this.idToken = tokens.IdToken;
    this.roles = getUserRoles(tokens.IdToken);
  }

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
