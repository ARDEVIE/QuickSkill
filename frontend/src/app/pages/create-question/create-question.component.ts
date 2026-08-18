import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
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

  constructor(
    private fb: FormBuilder,
    private forumService: ForumService,
    private courseService: CourseService,
    private router: Router
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
  }

  onSubmit(): void {
    if (this.questionForm.invalid) {
      this.errorMessage = 'Заполните все обязательные поля';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.forumService.createQuestion(this.questionForm.value).subscribe({
      next: (res) => {
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
