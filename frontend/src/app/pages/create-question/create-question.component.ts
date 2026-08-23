import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { ForumService } from 'src/app/core/services/forum.service';
import { CourseService, Category } from 'src/app/core/services/course.service';

@Component({
  selector: 'app-create-question',
  templateUrl: './create-question.component.html',
  styleUrls: ['./create-question.component.scss']
})
export class CreateQuestionComponent implements OnInit {
  questionForm: FormGroup;
  categories: Category[] = [];
  isLoading = false;
  errorMessage = '';
  selectedFile: File | null = null;
  editSlug: string | null = null;

  constructor(
    private fb: FormBuilder,
    private forumService: ForumService,
    private courseService: CourseService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.questionForm = this.fb.group({
      title: ['', Validators.required],
      content: ['', Validators.required],
      category: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    this.courseService.getCategories().subscribe(res => {
      this.categories = (res as any).results || res;
    });
    
    this.route.queryParams.subscribe(params => {
      if (params['edit']) {
        this.editSlug = params['edit'];
        this.loadQuestionForEdit();
      }
    });
  }

  loadQuestionForEdit(): void {
    if (!this.editSlug) return;
    this.isLoading = true;
    this.forumService.getQuestion(this.editSlug).subscribe({
      next: (q) => {
        this.questionForm.patchValue({
          title: q.title,
          content: q.content,
          category: q.category?.id || ''
        });
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Ошибка загрузки вопроса';
        this.isLoading = false;
      }
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
    }
  }

  onSubmit(): void {
    if (this.questionForm.invalid) {
      this.errorMessage = 'Заполните все обязательные поля';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const formData = new FormData();
    formData.append('title', this.questionForm.get('title')?.value);
    formData.append('content', this.questionForm.get('content')?.value);
    formData.append('category', this.questionForm.get('category')?.value);
    
    if (this.selectedFile) {
      formData.append('media_file', this.selectedFile);
    }

    if (this.editSlug) {
      this.forumService.updateQuestion(this.editSlug, formData).subscribe({
        next: (res: any) => {
          this.isLoading = false;
          this.router.navigate(['/forum', res.slug]);
        },
        error: () => {
          this.isLoading = false;
          this.errorMessage = 'Ошибка при сохранении вопроса';
        }
      });
    } else {
      this.forumService.createQuestion(formData).subscribe({
        next: (res: any) => {
          this.isLoading = false;
          this.router.navigate(['/forum', res.slug]);
        },
        error: () => {
          this.isLoading = false;
          this.errorMessage = 'Ошибка при создании вопроса';
        }
      });
    }
  }
}
