import { AbstractControl, ValidationErrors } from '@angular/forms';

export function passwordValidator(control: AbstractControl): ValidationErrors | null {
  const password = control.value as string;

  if (!password) return null;

  const minLength = /.{8,}/.test(password);
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=[\]{}|;:'",.<>/?]/.test(password);

  return minLength && hasUpper && hasLower && hasNumber && hasSpecial
    ? null
    : {
      cognitoPassword: {
        requirements:
          'Password must be at least 8 characters, include uppercase, lowercase, number, and special character'
      }
    };
}

export function passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
  const password = control.get('password')?.value;
  const confirmPassword = control.get('confirmPassword')?.value;

  return password === confirmPassword ? null : { mismatch: true };
}
