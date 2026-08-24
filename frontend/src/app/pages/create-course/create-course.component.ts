import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { CourseService, Category } from 'src/app/core/services/course.service';

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
    private router: Router
  ) {
    this.courseForm = this.fb.group({
      title: ['', Validators.required],
      category: ['', Validators.required],
      description: ['']
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

  onCancel(): void {
    this.router.navigate(['/courses']);
  }

  onSubmit(): void {
    if (this.courseForm.invalid) {
      this.errorMessage = 'Укажи название и предмет курса.';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const formData = new FormData();
    formData.append('title', this.courseForm.get('title')?.value);
    formData.append('description', this.courseForm.get('description')?.value || '');
    formData.append('category', this.courseForm.get('category')?.value);
    formData.append('is_published', 'false');

    if (this.selectedFile) {
      formData.append('cover', this.selectedFile);
    }

    this.courseService.createCourse(formData).subscribe({
      next: (course) => {
        this.isLoading = false;
        this.router.navigate(['/courses', course.id, 'edit']);
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'Ошибка при создании черновика';
      }
    });
  }
}
