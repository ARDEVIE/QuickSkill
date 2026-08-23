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

  // Rating Form
  isSubmitting = false;
  ratingForm: FormGroup;

  constructor(
    private route: ActivatedRoute,
    private courseService: CourseService,
    private authService: AuthService,
    private fb: FormBuilder
  ) {
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
        if (this.course) {
           this.course.ratings_count++;
        }
      },
      error: () => {
        this.isSubmitting = false;
        alert('Ошибка или вы уже оставили отзыв');
      }
    });
  }
}
