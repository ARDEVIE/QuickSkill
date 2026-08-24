import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Category } from 'src/app/core/services/course.service';
import { Resource, ResourceType, SubjectService } from 'src/app/core/services/subject.service';
import { AuthService } from 'src/app/core/services/auth.service';
import {
  RESOURCE_TAGS,
  ResourceTag,
  detectTypeFromFile,
  detectTypeFromUrl,
  resourceTypeLabel,
  titleFromFilename,
  titleFromUrl,
} from 'src/app/core/utils/resource-type.util';

@Component({
  selector: 'app-share-material',
  templateUrl: './share-material.component.html',
  styleUrls: ['./share-material.component.scss']
})
export class ShareMaterialComponent implements OnInit {
  form: FormGroup;
  categories: Category[] = [];

  selectedFile: File | null = null;
  detectedType: ResourceType | null = null;
  isDragging = false;
  private titleTouched = false;

  resourceTags: ResourceTag[] = RESOURCE_TAGS;
  selectedTags = new Set<string>();

  isSubmitting = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private subjectService: SubjectService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.form = this.fb.group({
      title: ['', Validators.required],
      category: ['', Validators.required],
      url: [''],
      description: ['']
    });
  }

  ngOnInit(): void {
    if (!this.authService.accessToken) {
      this.router.navigate(['/login']);
      return;
    }

    this.subjectService.getSubjects().subscribe(res => {
      this.categories = (res as any).results || res;
    });

    const subjectId = this.route.snapshot.queryParamMap.get('subject');
    if (subjectId) {
      this.form.patchValue({ category: subjectId });
    }
  }

  // ---------- File / URL (one combined input) ----------

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(): void {
    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
    const file = event.dataTransfer?.files?.[0];
    if (file) this.setFile(file);
  }

  onFileInputChange(event: any): void {
    const file = event.target.files?.[0];
    if (file) this.setFile(file);
  }

  private setFile(file: File): void {
    this.selectedFile = file;
    this.form.get('url')?.setValue('');
    this.detectedType = detectTypeFromFile(file);
    if (!this.titleTouched) {
      this.form.get('title')?.setValue(titleFromFilename(file.name));
    }
  }

  removeFile(): void {
    this.selectedFile = null;
    this.detectedType = null;
  }

  onUrlInput(value: string): void {
    this.selectedFile = null;
    if (!value.trim()) {
      this.detectedType = null;
      return;
    }
    this.detectedType = detectTypeFromUrl(value.trim());
    if (!this.titleTouched) {
      this.form.get('title')?.setValue(titleFromUrl(value.trim()));
    }
  }

  onTitleEdited(): void {
    this.titleTouched = true;
  }

  // ---------- Tags ----------

  toggleTag(value: string): void {
    if (this.selectedTags.has(value)) {
      this.selectedTags.delete(value);
    } else {
      this.selectedTags.add(value);
    }
  }

  isTagSelected(value: string): boolean {
    return this.selectedTags.has(value);
  }

  // ---------- Submit ----------

  resourceTypeLabel(type: ResourceType): string {
    return resourceTypeLabel(type);
  }

  submit(): void {
    if (this.form.invalid) return;

    const url = this.form.get('url')?.value?.trim();
    if (!this.selectedFile && !url) {
      this.errorMessage = 'Прикрепите файл или добавьте ссылку.';
      return;
    }

    this.isSubmitting = true;
    this.errorMessage = '';

    const formData = new FormData();
    formData.append('category', this.form.get('category')?.value);
    formData.append('title', this.form.get('title')?.value);
    formData.append('description', this.form.get('description')?.value || '');
    formData.append('type', this.detectedType || 'link');
    formData.append('tags', Array.from(this.selectedTags).join(','));

    if (this.selectedFile) {
      formData.append('file', this.selectedFile);
    } else {
      formData.append('url', url);
    }

    this.subjectService.createResource(formData).subscribe({
      next: (resource: Resource) => {
        this.isSubmitting = false;
        this.router.navigate(['/subjects', resource.category.id], { queryParams: { tab: 'materials' } });
      },
      error: () => {
        this.isSubmitting = false;
        this.errorMessage = 'Не удалось опубликовать материал.';
      }
    });
  }
}
