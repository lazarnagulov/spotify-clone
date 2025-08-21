import {Component} from '@angular/core';
import {AbstractControl, FormControl, FormGroup, ValidationErrors, Validators} from '@angular/forms';
import {AuthService} from '../auth.service';
import {RegisterResponse} from '../model/register-response.model';
import {ConfirmResponse} from '../model/confirm-response.model';

@Component({
  selector: 'app-register',
  standalone: false,
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  loading: boolean = false;
  codeSent: boolean = false;

  registerForm: FormGroup = new FormGroup({
    name: new FormControl('', Validators.required),
    surname: new FormControl('', Validators.required),
    birthdate: new FormControl('', Validators.required),
    username: new FormControl('', [Validators.required, Validators.minLength(4)]),
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required, Validators.minLength(6)]),
    confirmPassword: new FormControl('', Validators.required)
  }, { validators: this.passwordMatchValidator });

  codeForm: FormGroup = new FormGroup({
    code: new FormControl('', [Validators.required, Validators.minLength(6), Validators.maxLength(6)])
  })

  constructor(private authService: AuthService) {}

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('password')?.value;
    const confirmPassword = control.get('confirmPassword')?.value;

    return password === confirmPassword ? null : { mismatch: true };
  }

  onRegister(): void {
    if (this.registerForm.invalid) return;
    this.loading = true;

    this.authService.register({...this.registerForm.value}).subscribe({
      next: (result: RegisterResponse) => {
        this.loading = false;
        this.codeSent = true;
        console.log(result);
      },
      error: error => {
        this.loading = false;
        console.error(error)
      }
    });
  }

  onConfirmCode() {
    if (this.codeForm.invalid) return;

    this.loading = true;
    const request = {code: this.codeForm.value.code, username: this.registerForm.value.username}
    this.authService.confirm(request).subscribe({
      next: (result: ConfirmResponse) => {
        console.log(result);
      },
      error: error => {
        console.error(error)
      }
    })
  }

}
