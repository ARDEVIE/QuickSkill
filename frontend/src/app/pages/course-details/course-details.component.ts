import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
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
  authorInitials = '';
  authorName = '';

  isLoggedIn = false;
  isAuthor = false;
  isFavorited = false;
  currentUser: User | null = null;

  // Material Form
  showAddMaterial = false;
  materialForm: FormGroup;
  selectedFile: File | null = null;
  isSubmitting = false;

  // Rating Form
  ratingForm: FormGroup;

  constructor(
    private route: ActivatedRoute,
    private courseService: CourseService,
    private authService: AuthService,
    private fb: FormBuilder
  ) {
    this.materialForm = this.fb.group({
      title: ['', Validators.required],
      type: ['video_link', Validators.required],
      url: [''],
      file: [null]
    });

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
           this.authorInitials = (fn ? fn[0] : un[0]).toUpperCase() + (ln ? ln[0].toUpperCase() : '');
        }
        this.checkAuthor();
        // Assume backend doesn't tell us if it's favorited directly unless we fetch profile
        // For simplicity, we toggle blindly or manage state if needed.
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

  openTelegram(): void {
    if (this.course?.author?.telegram_url) {
      window.open(this.course.author.telegram_url, '_blank');
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

  onMaterialTypeChange(): void {
    const type = this.materialForm.get('type')?.value;
    if (type === 'video_link') {
      this.materialForm.get('url')?.setValidators([Validators.required]);
      this.materialForm.get('file')?.clearValidators();
    } else {
      this.materialForm.get('url')?.clearValidators();
      // file validator is custom handled via onFileSelect
    }
    this.materialForm.get('url')?.updateValueAndValidity();
    this.materialForm.get('file')?.updateValueAndValidity();
  }

  onFileSelect(event: any): void {
    if (event.target.files.length > 0) {
      this.selectedFile = event.target.files[0];
    }
  }

  onAddMaterial(): void {
    if (this.materialForm.invalid || !this.course) return;

    this.isSubmitting = true;
    const formData = new FormData();
    formData.append('title', this.materialForm.get('title')?.value);
    formData.append('type', this.materialForm.get('type')?.value);
    
    if (this.materialForm.get('type')?.value === 'video_link') {
      formData.append('url', this.materialForm.get('url')?.value);
    } else if (this.selectedFile) {
      formData.append('file', this.selectedFile);
    }

    this.courseService.addMaterial(this.course.id, formData).subscribe({
      next: (material) => {
        this.course?.materials.push(material);
        this.showAddMaterial = false;
        this.materialForm.reset({ type: 'video_link' });
        this.selectedFile = null;
        this.isSubmitting = false;
      },
      error: () => {
        this.isSubmitting = false;
        alert('Ошибка при добавлении материала');
      }
    });
  }

  onRateCourse(): void {
    if (this.ratingForm.invalid || !this.course) return;

    this.isSubmitting = true;
    const ratingData = {
      score: +this.ratingForm.get('score')?.value,
      comment: this.ratingForm.get('comment')?.value
    };

    this.courseService.rateCourse(this.course.id, ratingData).subscribe({
      next: (rating) => {
        this.course?.ratings.push(rating);
        this.ratingForm.reset({ score: '5' });
        this.isSubmitting = false;
        // Optionally update ratings_count and average_rating here
        if (this.course) {
           this.course.ratings_count++;
           // recalculate average_rating...
        }
      },
      error: () => {
        this.isSubmitting = false;
        alert('Ошибка или вы уже оставили отзыв');
      }
    });
  }
}
