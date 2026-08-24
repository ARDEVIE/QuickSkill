import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, ValidationErrors, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { CourseService, Category, MaterialType } from 'src/app/core/services/course.service';
import { AuthService } from 'src/app/core/services/auth.service';

interface DraftMaterial {
  title: string;
  type: MaterialType;
  url?: string;
  content?: string;
  file?: File | null;
}

interface DraftLesson {
  title: string;
  description: string;
  materials: DraftMaterial[];
}

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

  // Course content, built up client-side and created together with the course on submit.
  draftLessons: DraftLesson[] = [];

  showAddLesson = false;
  lessonForm: FormGroup;
  lessonError: string | null = null;

  activeMaterialLessonIndex: number | null = null;
  materialForm: FormGroup;
  selectedMaterialFile: File | null = null;

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

  materialTypeLabel(type: string): string {
    switch (type) {
      case 'pdf': return 'PDF документ';
      case 'video_link': return 'Видео';
      case 'link': return 'Ссылка';
      case 'text': return 'Текст';
      default: return type;
    }
  }

  openAddLesson(): void {
    this.lessonForm.reset();
    this.lessonError = null;
    this.showAddLesson = true;
  }

  onAddLesson(): void {
    if (this.lessonForm.invalid) return;

    this.draftLessons.push({
      title: this.lessonForm.value.title,
      description: this.lessonForm.value.description || '',
      materials: []
    });
    this.showAddLesson = false;
    this.lessonForm.reset();
    this.lessonError = null;
  }

  removeDraftLesson(index: number): void {
    this.draftLessons.splice(index, 1);
    if (this.activeMaterialLessonIndex === index) {
      this.activeMaterialLessonIndex = null;
    }
  }

  openAddMaterial(lessonIndex: number): void {
    this.activeMaterialLessonIndex = lessonIndex;
    this.selectedMaterialFile = null;
    this.materialForm.reset({ type: 'video_link' });
  }

  closeAddMaterial(): void {
    this.activeMaterialLessonIndex = null;
  }

  /** Runs on every value change (group validator) so the Save button reflects real validity as soon as the form opens. */
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
    if (type === 'pdf' && !this.selectedMaterialFile) {
      return { fileRequired: true };
    }
    return null;
  }

  onMaterialTypeChange(): void {
    this.selectedMaterialFile = null;
    this.materialForm.get('url')?.setValue('');
    this.materialForm.get('content')?.setValue('');
  }

  onMaterialFileSelect(event: any): void {
    if (event.target.files.length > 0) {
      this.selectedMaterialFile = event.target.files[0];
      this.materialForm.updateValueAndValidity();
    }
  }

  onAddMaterial(): void {
    if (this.materialForm.invalid || this.activeMaterialLessonIndex === null) return;

    const type: MaterialType = this.materialForm.value.type;
    this.draftLessons[this.activeMaterialLessonIndex].materials.push({
      title: this.materialForm.value.title,
      type,
      url: type === 'video_link' || type === 'link' ? this.materialForm.value.url : undefined,
      content: type === 'text' ? this.materialForm.value.content : undefined,
      file: type === 'pdf' ? this.selectedMaterialFile : null
    });

    this.activeMaterialLessonIndex = null;
    this.materialForm.reset({ type: 'video_link' });
    this.selectedMaterialFile = null;
  }

  removeDraftMaterial(lessonIndex: number, materialIndex: number): void {
    this.draftLessons[lessonIndex].materials.splice(materialIndex, 1);
  }

  async onSubmit(isPublished: boolean = true): Promise<void> {
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

    try {
      const course = await firstValueFrom(this.courseService.createCourse(formData));

      try {
        await this.saveDraftContent(course.id);
      } catch {
        // Course was created; content just didn't fully save — let the author finish it on the course page.
      }

      this.isLoading = false;
      this.router.navigate(['/courses', course.id]);
    } catch {
      this.isLoading = false;
      this.errorMessage = 'Ошибка при создании курса';
    }
  }

  private async saveDraftContent(courseId: number): Promise<void> {
    for (let i = 0; i < this.draftLessons.length; i++) {
      const draftLesson = this.draftLessons[i];
      const lesson = await firstValueFrom(this.courseService.createLesson(courseId, {
        title: draftLesson.title,
        description: draftLesson.description,
        order: i
      }));

      for (const draftMaterial of draftLesson.materials) {
        const materialData = new FormData();
        materialData.append('title', draftMaterial.title);
        materialData.append('type', draftMaterial.type);

        if (draftMaterial.type === 'video_link' || draftMaterial.type === 'link') {
          materialData.append('url', draftMaterial.url || '');
        } else if (draftMaterial.type === 'text') {
          materialData.append('content', draftMaterial.content || '');
        } else if (draftMaterial.type === 'pdf' && draftMaterial.file) {
          materialData.append('file', draftMaterial.file);
        }

        await firstValueFrom(this.courseService.addMaterialToLesson(lesson.id, materialData));
      }
    }
  }
}
