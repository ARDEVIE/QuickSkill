import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { CourseService, Category, CourseDetail } from 'src/app/core/services/course.service';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-edit-course',
  templateUrl: './edit-course.component.html',
  styleUrls: ['./edit-course.component.scss'] // You can create or use create-course styles
})
export class EditCourseComponent implements OnInit {
  courseForm: FormGroup;
  categories: Category[] = [];
  selectedFile: File | null = null;
  isLoading = false;
  errorMessage = '';
  courseId: number | null = null;
  course: CourseDetail | null = null;

  constructor(
    private fb: FormBuilder,
    private courseService: CourseService,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.courseForm = this.fb.group({
      title: ['', Validators.required],
      description: ['', Validators.required],
      category: ['', Validators.required],
      is_published: [false]
    });
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.courseId = +id;
      this.loadCourse(this.courseId);
    }
    
    this.courseService.getCategories().subscribe(res => {
      this.categories = (res as any).results || res;
    });
  }

  loadCourse(id: number): void {
    this.courseService.getCourse(id).subscribe({
      next: (course) => {
        this.course = course;
        this.courseForm.patchValue({
          title: course.title,
          description: course.description,
          category: course.category.id,
          is_published: course.is_published
        });
      },
      error: () => {
        this.router.navigate(['/courses']);
      }
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
    }
  }

  onSubmit(isPublished: boolean = true): void {
    if (this.courseForm.invalid || !this.courseId) {
      this.errorMessage = 'Заполните все обязательные поля';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const formData = new FormData();
    formData.append('title', this.courseForm.get('title')?.value);
    formData.append('description', this.courseForm.get('description')?.value);
    formData.append('category', this.courseForm.get('category')?.value);
    formData.append('is_published', String(isPublished));

    if (this.selectedFile) {
      formData.append('cover', this.selectedFile);
    }

    this.courseService.updateCourse(this.courseId, formData).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.router.navigate(['/courses', res.id]);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Ошибка при обновлении курса';
      }
    });
  }
}
