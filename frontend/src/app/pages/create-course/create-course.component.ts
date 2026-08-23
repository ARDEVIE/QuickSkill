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

  // Local state for builder
  sections: any[] = [];
  showSectionModal = false;
  showBlockModal = false;
  activeSectionIndex: number | null = null;

  sectionForm: FormGroup;
  blockForm: FormGroup;
  selectedBlockFile: File | null = null;

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

    this.sectionForm = this.fb.group({
      title: ['', Validators.required],
      order: [0]
    });

    this.blockForm = this.fb.group({
      type: ['video_link', Validators.required],
      content: [''],
      file: [null]
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

  onBlockFileSelect(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedBlockFile = file;
    }
  }

  onBlockTypeChange(): void {
    const type = this.blockForm.get('type')?.value;
    if (type === 'video_link' || type === 'text') {
      this.blockForm.get('content')?.setValidators([Validators.required]);
    } else {
      this.blockForm.get('content')?.clearValidators();
    }
    this.blockForm.get('content')?.updateValueAndValidity();
  }

  openSectionModal(): void {
    this.sectionForm.reset({ order: this.sections.length + 1 });
    this.showSectionModal = true;
  }

  onAddSection(): void {
    if (this.sectionForm.invalid) return;
    this.sections.push({
      ...this.sectionForm.value,
      blocks: []
    });
    this.showSectionModal = false;
  }

  openBlockModal(sectionIndex: number): void {
    this.activeSectionIndex = sectionIndex;
    this.blockForm.reset({ type: 'video_link' });
    this.selectedBlockFile = null;
    this.showBlockModal = true;
  }

  onAddBlock(): void {
    if (this.blockForm.invalid || this.activeSectionIndex === null) return;
    const type = this.blockForm.get('type')?.value;
    
    // Note: since we can't upload files inside a JSON array natively without multipart,
    // we would ideally need a multi-step upload. For this MVP, if type is 'pdf',
    // we'll just ignore the file in this local builder (since the backend doesn't support nested file upload via JSON).
    // The user can add pdfs later via 'edit-course'.
    
    this.sections[this.activeSectionIndex].blocks.push({
      type,
      content: type === 'video_link' || type === 'text' ? this.blockForm.get('content')?.value : '',
      file: type === 'media' ? this.selectedBlockFile : null
    });
    this.showBlockModal = false;
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

    if (this.sections.length > 0) {
      const sectionsForJson = this.sections.map((sec, sIdx) => {
        return {
          ...sec,
          blocks: sec.blocks.map((block: any, bIdx: number) => {
            if (block.file) {
              formData.append(`file_${sIdx}_${bIdx}`, block.file);
            }
            return {
              type: block.type,
              content: block.content
            };
          })
        };
      });
      formData.append('sections_data', JSON.stringify(sectionsForJson));
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
