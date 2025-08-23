import {Component, ViewChild} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {AuthService} from '../auth.service';
import {formatDate} from "@angular/common";
import {RegisterRequest} from "../model/register-request.model";
import {MatStepper} from "@angular/material/stepper";
import {ErrorResponse, ValidationDetail} from "../../shared/model/error-response.model";
import {passwordMatchValidator, passwordValidator} from "../validator/password.validator";

@Component({
  selector: 'app-register',
  standalone: false,
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  @ViewChild('stepper') stepper!: MatStepper;
  loading: boolean = false;
  codeSent: boolean = false;
  serverError: string | null = null;

  registerForm: FormGroup = new FormGroup({
    name: new FormControl('', Validators.required),
    family_name: new FormControl('', Validators.required),
    birthdate: new FormControl('', Validators.required),
    username: new FormControl('', [Validators.required, Validators.minLength(4)]),
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required, passwordValidator]),
    confirmPassword: new FormControl('', Validators.required)
  }, { validators: passwordMatchValidator });

  codeForm: FormGroup = new FormGroup({
    code: new FormControl('', [Validators.required, Validators.minLength(6), Validators.maxLength(6)])
  })

  constructor(private authService: AuthService) {}

  onRegister(): void {
    if (this.registerForm.invalid) return;
    this.loading = true;
    const rawBirthdate: Date = this.registerForm.value.birthdate;
    const formattedBirthdate = formatDate(rawBirthdate, 'yyyy-MM-dd', 'en-US');
    const request: RegisterRequest = {
      ...this.registerForm.value,
      birthdate: formattedBirthdate
    };

    this.authService.register(request).subscribe({
      next: _ => {
        this.loading = false;
        this.codeSent = true;
        this.stepper.next();
      },
      error: (error: ErrorResponse) => {
        this.loading = false;
        this.setError(error.error)
      }
    });
  }

  onConfirmCode() {
    if (this.codeForm.invalid) return;

    this.loading = true;
    const request = {code: this.codeForm.value.code, username: this.registerForm.value.username}
    this.authService.confirm(request).subscribe({
      next: _ => {
        this.loading = false;
        // TODO: Navigate
      },
      error: (error: ErrorResponse) => {
        this.loading = false;
        this.setError(error.error)
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
        if (this.registerForm.get(field)) {
          this.registerForm.get(field)?.setErrors({ serverError: err.msg });
        }
      });
    }
  }
}
