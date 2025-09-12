import { Component } from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {ErrorResponse, ValidationDetail} from '../../shared/model/error-response.model';
import {AuthService} from '../auth.service';
import {LoginResponse} from '../model/login-response.model';

@Component({
  selector: 'app-login',
  standalone: false,
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  loading: boolean = false;
  serverError: string | null = null;
  validationErrors: ValidationDetail[] | null = null;

  loginForm: FormGroup = new FormGroup({
    username: new FormControl('', [Validators.required]),
    password: new FormControl('', [Validators.required])
  });

  constructor(private authService: AuthService) {}

  onLogin(): void {
    if(this.loginForm.invalid) return;
    this.loading = true;
    this.authService.login(this.loginForm.value).subscribe({
      next: (response: LoginResponse) => {
        this.loading = false;
        this.authService.setTokens(response);
        // TODO: Navigate to home
      },
      error: (error: ErrorResponse) => {
        this.loading = false;
        this.setError(error.error);
      }
    });
  }


  private setError(error: string | ValidationDetail[]) {
    if (typeof error === 'string') {
      this.serverError = error;
    } else {
      this.serverError = null;
      error.forEach(err => {
        const field = err.loc[0];
        if (this.loginForm.get(field)) {
          this.loginForm.get(field)?.setErrors({ serverError: err.msg });
        }
      });
    }
  }
}
