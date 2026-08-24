import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService, User } from 'src/app/core/services/auth.service';
import { CourseService } from 'src/app/core/services/course.service';
import { ForumService } from 'src/app/core/services/forum.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
  user: User | null = null;
  isLoading = true;
  activeTab: 'info' | 'favorites' | 'edit' | 'my-courses' | 'drafts' | 'my-questions' = 'info';

  favorites: any[] = [];
  myCourses: any[] = [];
  drafts: any[] = [];
  myQuestions: any[] = [];
  
  profileForm: FormGroup;
  selectedAvatar: File | null = null;
  isSubmitting = false;

  constructor(
    private authService: AuthService,
    private courseService: CourseService,
    private forumService: ForumService,
    private router: Router,
    private route: ActivatedRoute,
    private fb: FormBuilder
  ) {
    this.profileForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: [''],
      bio: [''],
      telegram_username: ['']
    });
  }

  ngOnInit(): void {
    if (!this.authService.accessToken) {
      this.router.navigate(['/login']);
      return;
    }

    if (this.route.snapshot.queryParamMap.get('tab') === 'favorites') {
      this.setTab('favorites');
    }

    this.loadProfile();
  }

  loadProfile(): void {
    this.authService.fetchCurrentUser().subscribe({
      next: (u) => {
        this.user = u;
        this.isLoading = false;
        if (this.user) {
          this.profileForm.patchValue({
            first_name: this.user.first_name,
            last_name: this.user.last_name,
            bio: this.user.bio,
            telegram_username: this.user.telegram_username
          });
        }
      },
      error: () => {
        this.authService.clearAuth();
        this.router.navigate(['/login']);
      }
    });
  }

  setTab(tab: 'info' | 'favorites' | 'edit' | 'my-courses' | 'drafts' | 'my-questions'): void {
    this.activeTab = tab;
    if (tab === 'favorites' && this.favorites.length === 0) {
      this.authService.getFavorites().subscribe(res => {
        this.favorites = (res as any).results || res;
      });
    }
    if ((tab === 'my-courses' || tab === 'drafts') && this.myCourses.length === 0 && this.drafts.length === 0 && this.user) {
      this.courseService.getCourses({ author: this.user.id }).subscribe(res => {
        const allCourses = res.results || [];
        this.myCourses = allCourses.filter((c: any) => c.is_published);
        this.drafts = allCourses.filter((c: any) => !c.is_published);
      });
    }
    if (tab === 'my-questions' && this.myQuestions.length === 0 && this.user) {
      this.forumService.getQuestions({ author: this.user.id }).subscribe((res: any) => {
        this.myQuestions = res.results || [];
      });
    }
  }

  deleteCourse(id: number): void {
    if (confirm('Вы уверены, что хотите удалить этот курс?')) {
      this.courseService.deleteCourse(id).subscribe({
        next: () => {
          this.myCourses = this.myCourses.filter((c: any) => c.id !== id);
          this.drafts = this.drafts.filter((c: any) => c.id !== id);
        },
        error: () => alert('Ошибка при удалении курса')
      });
    }
  }

  deleteQuestion(slug: string): void {
    if (confirm('Вы уверены, что хотите удалить этот вопрос?')) {
      this.forumService.deleteQuestion(slug).subscribe({
        next: () => {
          this.myQuestions = this.myQuestions.filter((q: any) => q.slug !== slug);
        },
        error: () => alert('Ошибка при удалении вопроса')
      });
    }
  }

  onAvatarSelect(event: any): void {
    if (event.target.files.length > 0) {
      this.selectedAvatar = event.target.files[0];
    }
  }

  onSaveProfile(): void {
    if (this.profileForm.invalid) return;

    this.isSubmitting = true;
    const formData = new FormData();
    formData.append('first_name', this.profileForm.get('first_name')?.value);
    formData.append('last_name', this.profileForm.get('last_name')?.value);
    formData.append('bio', this.profileForm.get('bio')?.value);
    formData.append('telegram_username', this.profileForm.get('telegram_username')?.value || '');

    if (this.selectedAvatar) {
      formData.append('avatar', this.selectedAvatar);
    }

    this.authService.updateProfile(formData).subscribe({
      next: (user) => {
        this.user = user;
        this.isSubmitting = false;
        this.setTab('info');
      },
      error: () => {
        this.isSubmitting = false;
        alert('Ошибка при сохранении профиля');
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }
}
