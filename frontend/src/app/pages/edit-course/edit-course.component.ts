import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { CourseService, Category, CourseDetail, Section, ContentBlock } from 'src/app/core/services/course.service';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-edit-course',
  templateUrl: './edit-course.component.html',
  styleUrls: ['./edit-course.component.scss']
})
export class EditCourseComponent implements OnInit {
  courseForm: FormGroup;
  categories: Category[] = [];
  selectedFile: File | null = null;
  isLoading = false;
  errorMessage = '';
  courseId: number | null = null;
  course: CourseDetail | null = null;

  // Modals for Builder
  showSectionModal = false;
  showBlockModal = false;
  activeSectionId: number | null = null;

  sectionForm: FormGroup;
  blockForm: FormGroup;
  selectedBlockFile: File | null = null;
  isSubmittingSection = false;
  isSubmittingBlock = false;

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
          category: course.category?.id || '',
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

  onSubmitCourse(): void {
    if (this.courseForm.invalid || !this.courseId) {
      this.errorMessage = 'Заполните все обязательные поля';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const formData = new FormData();
    formData.append('title', this.courseForm.get('title')?.value);
    formData.append('description', this.courseForm.get('description')?.value);
    
    const catVal = this.courseForm.get('category')?.value;
    if (catVal) {
       formData.append('category', catVal);
    }
    
    formData.append('is_published', this.courseForm.get('is_published')?.value);

    if (this.selectedFile) {
      formData.append('cover', this.selectedFile);
    }

    this.courseService.updateCourse(this.courseId, formData).subscribe({
      next: (res) => {
        this.isLoading = false;
        alert('Курс успешно обновлен');
        this.loadCourse(this.courseId!);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = 'Ошибка при обновлении курса';
      }
    });
  }

  openSectionModal(): void {
    this.sectionForm.reset({ order: (this.course?.sections?.length || 0) + 1 });
    this.showSectionModal = true;
  }

  onAddSection(): void {
    if (this.sectionForm.invalid || !this.courseId) return;
    this.isSubmittingSection = true;
    
    this.courseService.addSection(this.courseId, this.sectionForm.value).subscribe({
      next: (sec) => {
        if (!this.course!.sections) this.course!.sections = [];
        this.course!.sections.push(sec);
        this.showSectionModal = false;
        this.isSubmittingSection = false;
      },
      error: () => {
        this.isSubmittingSection = false;
        alert('Ошибка при добавлении модуля');
      }
    });
  }

  openBlockModal(sectionId: number): void {
    this.activeSectionId = sectionId;
    this.blockForm.reset({ type: 'video_link' });
    this.selectedBlockFile = null;
    this.showBlockModal = true;
  }

  onAddBlock(): void {
    if (this.blockForm.invalid || !this.activeSectionId) return;
    this.isSubmittingBlock = true;
    
    const formData = new FormData();
    formData.append('type', this.blockForm.get('type')?.value);
    
    const type = this.blockForm.get('type')?.value;
    if (type === 'video_link' || type === 'text') {
       formData.append('content', this.blockForm.get('content')?.value);
    }
    if (type === 'media' && this.selectedBlockFile) {
       formData.append('file', this.selectedBlockFile);
    }

    this.courseService.addBlock(this.activeSectionId, formData).subscribe({
      next: (block) => {
        const section = this.course?.sections?.find(s => s.id === this.activeSectionId);
        if (section) {
          if (!section.blocks) section.blocks = [];
          section.blocks.push(block);
        }
        this.showBlockModal = false;
        this.isSubmittingBlock = false;
      },
      error: () => {
        this.isSubmittingBlock = false;
        alert('Ошибка при добавлении контента');
      }
    });
  }
}
