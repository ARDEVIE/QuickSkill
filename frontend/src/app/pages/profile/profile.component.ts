import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService, User } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
  user: User | null = null;
  isLoading = true;

  isEditing = false;
  isSaving = false;
  errorMessage: string | null = null;
  editForm: FormGroup;
  selectedAvatarFile: File | null = null;

  constructor(
    private authService: AuthService,
    private router: Router,
    private fb: FormBuilder
  ) {
    this.editForm = this.fb.group({
      first_name: [''],
      last_name: [''],
      bio: [''],
      telegram_username: ['']
    }, { validators: [] });
  }

  ngOnInit(): void {
    if (!this.authService.accessToken) {
      this.router.navigate(['/login']);
      return;
    }

    this.authService.fetchCurrentUser().subscribe({
      next: (u) => {
        this.user = u;
        this.isLoading = false;
      },
      error: () => {
        this.authService.clearAuth();
        this.router.navigate(['/login']);
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }

  startEdit(): void {
    if (!this.user) return;
    this.editForm.setValue({
      first_name: this.user.first_name || '',
      last_name: this.user.last_name || '',
      bio: this.user.bio || '',
      telegram_username: this.user.telegram_username || ''
    });
    this.selectedAvatarFile = null;
    this.errorMessage = null;
    this.isEditing = true;
  }

  cancelEdit(): void {
    this.isEditing = false;
    this.errorMessage = null;
  }

  onAvatarSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedAvatarFile = input.files[0];
    }
  }

  onSave(): void {
    this.isSaving = true;
    this.errorMessage = null;

    const formData = new FormData();
    Object.entries(this.editForm.value).forEach(([key, value]) => {
      formData.append(key, (value as string) ?? '');
    });
    if (this.selectedAvatarFile) {
      formData.append('avatar', this.selectedAvatarFile);
    }

    this.authService.updateProfile(formData).subscribe({
      next: (user) => {
        this.user = user;
        this.isSaving = false;
        this.isEditing = false;
      },
      error: () => {
        this.isSaving = false;
        this.errorMessage = 'Не удалось сохранить изменения';
      }
    });
  }
}
