import { Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { ErrorResponse, ValidationDetail } from './model/error-response.model';

@Injectable({
  providedIn: 'root'
})
export class ErrorHandlerService {

  constructor() { }

  handleError(error: HttpErrorResponse): ErrorResponse {
    let err: ErrorResponse;

    if (error.error) {
      err = error.error as ErrorResponse;
    } else {
      err = {
        status: error.status,
        error: [{loc: [], msg: 'Unknown error', type: 'unknown_error'}] as ValidationDetail[]
      };
    }

    return err;
  }
}
