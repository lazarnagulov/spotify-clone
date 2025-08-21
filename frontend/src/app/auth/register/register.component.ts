import {Component} from '@angular/core';
import {AbstractControl, FormControl, FormGroup, ValidationErrors, Validators} from '@angular/forms';

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

  constructor() {}

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('password')?.value;
    const confirmPassword = control.get('confirmPassword')?.value;

    return password === confirmPassword ? null : { mismatch: true };
  }

  onRegister(): void {
    if (this.registerForm.invalid) return;

    this.loading = true;
    setTimeout(() => {
      this.loading = false;
      this.codeSent = true;
    }, 1500);
  }

  onConfirmCode() {
    if (this.codeForm.invalid) return;

    this.loading = true;
    setTimeout(() => {
      this.loading = false;
      alert('Registration complete!');
    }, 1200);
  }

}
