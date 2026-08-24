import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { CourseService, Category } from 'src/app/core/services/course.service';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-create-course',
  templateUrl: './create-course.component.html',
  styleUrls: ['./create-course.component.scss']
})
export class CreateCourseComponent implements OnInit {
  courseForm: FormGroup;
  categories: Category[] = [];
  selectedFile: File | null = null;
  isLoading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private courseService: CourseService,
    private authService: AuthService,
    private router: Router
  ) {
    this.courseForm = this.fb.group({
      title: ['', Validators.required],
      description: ['', Validators.required],
      category: ['', Validators.required],
      is_published: [false]
    });
  }

  ngOnInit(): void {
    this.courseService.getCategories().subscribe(res => {
      this.categories = (res as any).results || res;
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
    }
  }

  onSubmit(isPublished: boolean = true): void {
    if (this.courseForm.invalid) {
      if (!this.courseForm.get('category')?.value) {
        this.errorMessage = 'Пожалуйста, выберите категорию курса.';
      } else {
        this.errorMessage = 'Заполните все обязательные поля';
      }
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const formData = new FormData();
    formData.append('title', this.courseForm.get('title')?.value);
    formData.append('description', this.courseForm.get('description')?.value);
    const categoryValue = this.courseForm.get('category')?.value;
    if (categoryValue) {
      formData.append('category', categoryValue);
    }
    formData.append('is_published', isPublished ? 'true' : 'false');

    if (this.selectedFile) {
      formData.append('cover', this.selectedFile);
    }

    this.courseService.createCourse(formData).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.router.navigate(['/courses', res.id]);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Ошибка при создании курса';
      }
    });
  }
}
