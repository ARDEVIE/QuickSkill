import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AbstractControl, FormBuilder, FormGroup, ValidationErrors, Validators } from '@angular/forms';
import { CourseService, CourseDetail } from 'src/app/core/services/course.service';
import { AuthService, User } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-course-details',
  templateUrl: './course-details.component.html',
  styleUrls: ['./course-details.component.scss']
})
export class CourseDetailsComponent implements OnInit {
  course: CourseDetail | null = null;
  isLoading = true;
  authorName = '';

  isLoggedIn = false;
  isAuthor = false;
  isFavorited = false;
  currentUser: User | null = null;

  // Lesson form (author only)
  showAddLesson = false;
  lessonForm: FormGroup;
  lessonError: string | null = null;

  // Material form (author only) — scoped to whichever lesson is currently open
  activeMaterialLessonId: number | null = null;
  materialForm: FormGroup;
  selectedFile: File | null = null;
  isSubmitting = false;
  materialError: string | null = null;

  // Rating Form
  ratingForm: FormGroup;
  ratingError: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private courseService: CourseService,
    private authService: AuthService,
    private fb: FormBuilder
  ) {
    this.lessonForm = this.fb.group({
      title: ['', Validators.required],
      description: ['']
    });

    this.materialForm = this.fb.group({
      title: ['', Validators.required],
      type: ['video_link', Validators.required],
      url: [''],
      content: [''],
      file: [null]
    }, { validators: (group: AbstractControl): ValidationErrors | null => this.validateMaterialForm(group) });

    this.ratingForm = this.fb.group({
      score: ['5', Validators.required],
      comment: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');

    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      this.isLoggedIn = !!user;
      this.checkAuthor();
    });

    if (id) {
      this.loadCourse(+id);
    }
  }

  loadCourse(id: number): void {
    this.courseService.getCourse(id).subscribe({
      next: (data) => {
        this.course = data;
        this.isLoading = false;

        if (this.course.author) {
           const fn = this.course.author.first_name;
           const ln = this.course.author.last_name;
           const un = this.course.author.username;
           this.authorName = (fn || un) + (ln ? ' ' + ln : '');
        }
        this.checkAuthor();
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  checkAuthor(): void {
    if (this.course && this.currentUser) {
      this.isAuthor = this.course.author.id === this.currentUser.id;
    }
  }

  toggleFavorite(): void {
    if (!this.course) return;
    this.courseService.toggleFavorite(this.course.id).subscribe({
      next: (res) => {
        this.isFavorited = res.favorited;
      }
    });
  }

  totalMaterialsCount(): number {
    if (!this.course) return 0;
    const inLessons = this.course.lessons.reduce((sum, l) => sum + l.materials.length, 0);
    return inLessons + this.course.materials.length;
  }

  materialTypeLabel(type: string): string {
    switch (type) {
      case 'pdf': return 'PDF документ';
      case 'video_link': return 'Видео';
      case 'link': return 'Ссылка';
      case 'text': return 'Текст';
      default: return type;
    }
  }

  onAddLesson(): void {
    if (this.lessonForm.invalid || !this.course) return;

    this.isSubmitting = true;
    this.lessonError = null;

    this.courseService.createLesson(this.course.id, {
      title: this.lessonForm.value.title,
      description: this.lessonForm.value.description,
      order: this.course.lessons.length
    }).subscribe({
      next: (lesson) => {
        this.course?.lessons.push(lesson);
        this.showAddLesson = false;
        this.lessonForm.reset();
        this.isSubmitting = false;
      },
      error: () => {
        this.isSubmitting = false;
        this.lessonError = 'Ошибка при добавлении урока';
      }
    });
  }

  openAddMaterial(lessonId: number): void {
    this.activeMaterialLessonId = lessonId;
    this.materialError = null;
    this.selectedFile = null;
    this.materialForm.reset({ type: 'video_link' });
  }

  closeAddMaterial(): void {
    this.activeMaterialLessonId = null;
  }

  /**
   * Runs on every value change (group validator), not just on the type
   * <select>'s (change) event — so the button reflects real validity from
   * the moment the form opens, including for the default type.
   */
  validateMaterialForm(group: AbstractControl): ValidationErrors | null {
    const type = group.get('type')?.value;
    const url = group.get('url')?.value;
    const content = group.get('content')?.value;

    if ((type === 'video_link' || type === 'link') && !url) {
      return { urlRequired: true };
    }
    if (type === 'text' && !content) {
      return { contentRequired: true };
    }
    if (type === 'pdf' && !this.selectedFile) {
      return { fileRequired: true };
    }
    return null;
  }

  onMaterialTypeChange(): void {
    // Field values change under the type switch (e.g. a previously picked
    // PDF no longer applies once you switch to "text") — clear them so
    // validity isn't based on a stale value from a different type.
    this.selectedFile = null;
    this.materialForm.get('url')?.setValue('');
    this.materialForm.get('content')?.setValue('');
  }

  onFileSelect(event: any): void {
    if (event.target.files.length > 0) {
      this.selectedFile = event.target.files[0];
      this.materialForm.updateValueAndValidity();
    }
  }

  onAddMaterial(): void {
    if (this.materialForm.invalid || !this.course || this.activeMaterialLessonId === null) return;

    this.isSubmitting = true;
    this.materialError = null;
    const type = this.materialForm.get('type')?.value;

    const formData = new FormData();
    formData.append('title', this.materialForm.get('title')?.value);
    formData.append('type', type);

    if (type === 'video_link' || type === 'link') {
      formData.append('url', this.materialForm.get('url')?.value);
    } else if (type === 'text') {
      formData.append('content', this.materialForm.get('content')?.value);
    } else if (type === 'pdf' && this.selectedFile) {
      formData.append('file', this.selectedFile);
    }

    const lessonId = this.activeMaterialLessonId;

    this.courseService.addMaterialToLesson(lessonId, formData).subscribe({
      next: (material) => {
        const lesson = this.course?.lessons.find(l => l.id === lessonId);
        lesson?.materials.push(material);
        this.activeMaterialLessonId = null;
        this.materialForm.reset({ type: 'video_link' });
        this.selectedFile = null;
        this.isSubmitting = false;
      },
      error: () => {
        this.isSubmitting = false;
        this.materialError = 'Ошибка при добавлении материала';
      }
    });
  }

  onRateCourse(): void {
    if (this.ratingForm.invalid || !this.course) return;

    this.isSubmitting = true;
    this.ratingError = null;
    const ratingData = {
      score: +this.ratingForm.get('score')?.value,
      comment: this.ratingForm.get('comment')?.value
    };

    this.courseService.rateCourse(this.course.id, ratingData).subscribe({
      next: (rating) => {
        this.course?.ratings.push(rating);
        this.ratingForm.reset({ score: '5' });
        this.isSubmitting = false;
        if (this.course) {
           this.course.ratings_count++;
        }
      },
      error: () => {
        this.isSubmitting = false;
        this.ratingError = 'Ошибка или вы уже оставили отзыв';
      }
    });
  }
}
