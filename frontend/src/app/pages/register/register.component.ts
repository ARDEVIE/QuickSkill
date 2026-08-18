import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  registerForm: FormGroup;
  errorMessage: string | null = null;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required],
      terms: [false, Validators.requiredTrue]
    }, { validators: this.passwordMatchValidator });
  }

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('password')?.value;
    const confirmPassword = control.get('confirmPassword')?.value;
    if (password !== confirmPassword) {
      return { passwordMismatch: true };
    }
    return null;
  }

  onSubmit(): void {
    if (this.registerForm.invalid) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = null;

    const formValue = this.registerForm.value;
    // Auto-generate username from email to preserve UI
    const generatedUsername = formValue.email.split('@')[0] + Math.floor(Math.random() * 10000);

    const payload = {
      first_name: formValue.name,
      email: formValue.email,
      password: formValue.password,
      username: generatedUsername
    };

    this.authService.register(payload).subscribe({
      next: () => {
        // Automatically login after successful registration
        this.authService.login({ email: formValue.email, password: formValue.password }).subscribe({
          next: () => {
            this.isLoading = false;
            this.router.navigate(['/courses']);
          },
          error: () => {
            this.isLoading = false;
            this.router.navigate(['/login']);
          }
        });
      },
      error: (err) => {
        this.isLoading = false;
        if (err.error && typeof err.error === 'object') {
          // Flatten error messages if provided by DRF
          this.errorMessage = Object.values(err.error).flat().join(', ');
        } else {
          this.errorMessage = 'Произошла ошибка при регистрации';
        }
      }
    });
  }
}
