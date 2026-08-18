import { Component, OnInit } from '@angular/core';
import { ForumService, Question } from 'src/app/core/services/forum.service';
import { CourseService, Category } from 'src/app/core/services/course.service';

@Component({
  selector: 'app-forum-list',
  templateUrl: './forum-list.component.html',
  styleUrls: ['./forum-list.component.scss']
})
export class ForumListComponent implements OnInit {
  questions: Question[] = [];
  categories: Category[] = [];
  totalQuestions = 0;
  searchQuery = '';
  activeCategory: number | null = null;
  searchTimeout: any;

  constructor(
    private forumService: ForumService,
    private courseService: CourseService
  ) {}

  ngOnInit(): void {
    this.courseService.getCategories().subscribe(res => {
      this.categories = (res as any).results || res;
    });
    this.loadQuestions();
  }

  loadQuestions(): void {
    const params: any = {};
    if (this.searchQuery) params.search = this.searchQuery;
    if (this.activeCategory) params.category = this.activeCategory;

    this.forumService.getQuestions(params).subscribe(res => {
      this.questions = res.results;
      this.totalQuestions = res.count;
    });
  }

  onSearch(event: any): void {
    this.searchQuery = event.target.value;
    clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(() => {
      this.loadQuestions();
    }, 500);
  }

  setCategory(categoryId: number | null): void {
    this.activeCategory = categoryId;
    this.loadQuestions();
  }
}
