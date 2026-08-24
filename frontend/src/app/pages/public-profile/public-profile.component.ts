import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService, User } from 'src/app/core/services/auth.service';
import { CourseService, Course } from 'src/app/core/services/course.service';
import { SubjectService, Resource } from 'src/app/core/services/subject.service';
import { ForumService, Question, Comment } from 'src/app/core/services/forum.service';

type Tab = 'overview' | 'courses' | 'materials' | 'answers' | 'questions' | 'saved';

interface ActivityItem {
  kind: 'course' | 'material' | 'answer' | 'question';
  title: string;
  subtitle: string;
  date: string;
  route: any[];
  queryParams?: any;
}

@Component({
  selector: 'app-public-profile',
  templateUrl: './public-profile.component.html',
  styleUrls: ['./public-profile.component.scss']
})
export class PublicProfileComponent implements OnInit {
  user: User | null = null;
  currentUser: User | null = null;
  isOwner = false;
  isLoading = true;
  activeTab: Tab = 'overview';
  isEditing = false;

  // Overview
  isLoadingOverview = false;
  private overviewLoadedOnce = false;
  overviewCourses: Course[] = [];
  overviewMaterials: Resource[] = [];
  overviewAnswers: Comment[] = [];
  recentActivity: ActivityItem[] = [];

  // Courses
  courses: Course[] = [];
  drafts: Course[] = [];
  isLoadingCourses = false;
  private coursesLoadedOnce = false;

  // Materials
  materials: Resource[] = [];
  isLoadingMaterials = false;
  private materialsLoadedOnce = false;

  // Answers
  answers: Comment[] = [];
  isLoadingAnswers = false;
  private answersLoadedOnce = false;

  // Questions
  questions: Question[] = [];
  isLoadingQuestions = false;
  private questionsLoadedOnce = false;

  // Saved (owner only)
  savedCourses: Course[] = [];
  savedQuestions: Question[] = [];
  isLoadingSaved = false;
  private savedLoadedOnce = false;

  profileForm: FormGroup;
  selectedAvatar: File | null = null;
  isSubmitting = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private courseService: CourseService,
    private subjectService: SubjectService,
    private forumService: ForumService,
    private fb: FormBuilder
  ) {
    this.profileForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: [''],
      bio: [''],
      study_program: [''],
      study_year: [''],
      telegram_username: ['']
    });
  }

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(u => {
      this.currentUser = u;
      this.refreshIsOwner();
    });

    this.route.paramMap.subscribe(params => {
      this.loadProfile(params.get('username'));
    });
  }

  private refreshIsOwner(): void {
    this.isOwner = !!this.currentUser && !!this.user && this.currentUser.username === this.user.username;
  }

  private loadProfile(username: string | null): void {
    this.isLoading = true;
    this.resetTabState();

    if (!username) {
      if (!this.authService.accessToken) {
        this.router.navigate(['/login']);
        return;
      }
      this.authService.fetchCurrentUser().subscribe({
        next: (u) => this.onProfileLoaded(u),
        error: () => {
          this.authService.clearAuth();
          this.router.navigate(['/login']);
        }
      });
    } else {
      this.authService.getPublicProfile(username).subscribe({
        next: (u) => this.onProfileLoaded(u),
        error: () => this.router.navigate(['/'])
      });
    }
  }

  private onProfileLoaded(u: User): void {
    this.user = u;
    this.isLoading = false;
    this.refreshIsOwner();
    this.profileForm.patchValue({
      first_name: u.first_name,
      last_name: u.last_name,
      bio: u.bio,
      study_program: u.study_program,
      study_year: u.study_year || '',
      telegram_username: u.telegram_username
    });
    this.setTab('overview');
  }

  private resetTabState(): void {
    this.activeTab = 'overview';
    this.isEditing = false;
    this.overviewLoadedOnce = false;
    this.coursesLoadedOnce = false;
    this.materialsLoadedOnce = false;
    this.answersLoadedOnce = false;
    this.questionsLoadedOnce = false;
    this.savedLoadedOnce = false;
  }

  setTab(tab: Tab): void {
    this.activeTab = tab;
    this.isEditing = false;
    if (tab === 'overview' && !this.overviewLoadedOnce) this.loadOverview();
    if (tab === 'courses' && !this.coursesLoadedOnce) this.loadCourses();
    if (tab === 'materials' && !this.materialsLoadedOnce) this.loadMaterials();
    if (tab === 'answers' && !this.answersLoadedOnce) this.loadAnswers();
    if (tab === 'questions' && !this.questionsLoadedOnce) this.loadQuestions();
    if (tab === 'saved' && !this.savedLoadedOnce && this.isOwner) this.loadSaved();
  }

  // ---------- Overview ----------

  private loadOverview(): void {
    if (!this.user) return;
    this.overviewLoadedOnce = true;
    this.isLoadingOverview = true;
    let pending = 4;
    const done = () => { if (--pending === 0) this.buildRecentActivity(); };

    this.courseService.getCourses({ author: this.user.id, public_only: 'true' }).subscribe({
      next: (res) => { this.overviewCourses = (res.results || []).slice(0, 3); done(); },
      error: done
    });

    this.subjectService.getResources({ author: this.user.id }).subscribe({
      next: (res) => { this.overviewMaterials = ((res as any).results || res).slice(0, 3); done(); },
      error: done
    });

    this.forumService.getUserAnswers(this.user.id).subscribe({
      next: (res) => {
        const all = ((res as any).results || res) as Comment[];
        this.overviewAnswers = [...all]
          .sort((a, b) => (Number(b.is_accepted) - Number(a.is_accepted)) || (b.vote_score - a.vote_score))
          .slice(0, 3);
        done();
      },
      error: done
    });

    this.forumService.getQuestions({ author: this.user.id }).subscribe({
      next: (res) => { this.overviewQuestionsCache = (res.results || []); done(); },
      error: done
    });
  }

  private overviewQuestionsCache: Question[] = [];

  private buildRecentActivity(): void {
    this.isLoadingOverview = false;
    const items: ActivityItem[] = [];

    this.overviewCourses.forEach(c => items.push({
      kind: 'course', title: c.title, subtitle: 'Курс', date: c.created_at,
      route: ['/courses', c.id]
    }));
    this.overviewMaterials.forEach(m => items.push({
      kind: 'material', title: m.title, subtitle: 'Материал', date: m.created_at,
      route: ['/subjects', m.category.id], queryParams: { tab: 'materials' }
    }));
    this.overviewAnswers.forEach(a => items.push({
      kind: 'answer', title: a.question_title || 'Ответ на вопрос', subtitle: 'Ответ', date: a.created_at,
      route: ['/forum', a.question_slug]
    }));
    this.overviewQuestionsCache.forEach(q => items.push({
      kind: 'question', title: q.title, subtitle: 'Вопрос', date: q.created_at,
      route: ['/forum', q.slug]
    }));

    this.recentActivity = items
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, 5);
  }

  // ---------- Courses ----------

  private loadCourses(): void {
    if (!this.user) return;
    this.coursesLoadedOnce = true;
    this.isLoadingCourses = true;
    this.courseService.getCourses({ author: this.user.id }).subscribe({
      next: (res) => {
        const all = res.results || [];
        this.courses = all.filter(c => c.is_published);
        this.drafts = all.filter(c => !c.is_published);
        this.isLoadingCourses = false;
      },
      error: () => this.isLoadingCourses = false
    });
  }

  deleteCourse(id: number): void {
    if (!confirm('Удалить этот курс?')) return;
    this.courseService.deleteCourse(id).subscribe(() => {
      this.courses = this.courses.filter(c => c.id !== id);
      this.drafts = this.drafts.filter(c => c.id !== id);
    });
  }

  // ---------- Materials ----------

  private loadMaterials(): void {
    if (!this.user) return;
    this.materialsLoadedOnce = true;
    this.isLoadingMaterials = true;
    this.subjectService.getResources({ author: this.user.id }).subscribe({
      next: (res) => {
        this.materials = (res as any).results || res;
        this.isLoadingMaterials = false;
      },
      error: () => this.isLoadingMaterials = false
    });
  }

  // ---------- Answers ----------

  private loadAnswers(): void {
    if (!this.user) return;
    this.answersLoadedOnce = true;
    this.isLoadingAnswers = true;
    this.forumService.getUserAnswers(this.user.id).subscribe({
      next: (res) => {
        this.answers = (res as any).results || res;
        this.isLoadingAnswers = false;
      },
      error: () => this.isLoadingAnswers = false
    });
  }

  // ---------- Questions ----------

  private loadQuestions(): void {
    if (!this.user) return;
    this.questionsLoadedOnce = true;
    this.isLoadingQuestions = true;
    this.forumService.getQuestions({ author: this.user.id }).subscribe({
      next: (res) => {
        this.questions = res.results || [];
        this.isLoadingQuestions = false;
      },
      error: () => this.isLoadingQuestions = false
    });
  }

  deleteQuestion(slug: string): void {
    if (!confirm('Удалить этот вопрос?')) return;
    this.forumService.deleteQuestion(slug).subscribe(() => {
      this.questions = this.questions.filter(q => q.slug !== slug);
    });
  }

  // ---------- Saved ----------

  private loadSaved(): void {
    this.savedLoadedOnce = true;
    this.isLoadingSaved = true;
    let pending = 2;
    const done = () => { if (--pending === 0) this.isLoadingSaved = false; };

    this.authService.getFavorites().subscribe({
      next: (res) => { this.savedCourses = (res as any).results || res; done(); },
      error: done
    });
    this.forumService.getFavoriteQuestions().subscribe({
      next: (res) => { this.savedQuestions = (res as any).results || res; done(); },
      error: done
    });
  }

  // ---------- Edit ----------

  toggleEdit(): void {
    this.isEditing = !this.isEditing;
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
    formData.append('last_name', this.profileForm.get('last_name')?.value || '');
    formData.append('bio', this.profileForm.get('bio')?.value || '');
    formData.append('study_program', this.profileForm.get('study_program')?.value || '');
    formData.append('study_year', this.profileForm.get('study_year')?.value || '');
    formData.append('telegram_username', this.profileForm.get('telegram_username')?.value || '');
    if (this.selectedAvatar) formData.append('avatar', this.selectedAvatar);

    this.authService.updateProfile(formData).subscribe({
      next: (user) => {
        this.user = user;
        this.isSubmitting = false;
        this.isEditing = false;
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
