import { Component, OnInit } from '@angular/core';
import { ForumService, Question } from 'src/app/core/services/forum.service';
import { CourseService, Category } from 'src/app/core/services/course.service';
import { AuthService, User } from 'src/app/core/services/auth.service';

type TabFilter = 'new' | 'mine' | 'popular' | 'unanswered';

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
  activeTab: TabFilter = 'new';
  currentUser: User | null = null;
  isLoading = true;
  private searchTimeout: any;

  constructor(
    private forumService: ForumService,
    private courseService: CourseService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    this.courseService.getCategories().subscribe(res => {
      this.categories = (res as any).results || res;
    });
    this.loadQuestions();
  }

  loadQuestions(): void {
    this.isLoading = true;
    const params: any = {};
    if (this.searchQuery) params.search = this.searchQuery;
    if (this.activeCategory) params.category = this.activeCategory;
    if (this.activeTab !== 'new') params.filter = this.activeTab;

    this.forumService.getQuestions(params).subscribe({
      next: (res) => {
        this.questions = res.results;
        this.totalQuestions = res.count;
        this.isLoading = false;
      },
      error: () => this.isLoading = false
    });
  }

  onSearch(event: any): void {
    this.searchQuery = event.target.value;
    clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(() => this.loadQuestions(), 400);
  }

  setTab(tab: TabFilter): void {
    if (tab === 'mine' && !this.currentUser) return;
    this.activeTab = tab;
    this.loadQuestions();
  }

  setCategory(categoryId: number | null): void {
    this.activeCategory = categoryId;
    this.loadQuestions();
  }

  questionTags(question: Question): string[] {
    return (question.tags || '').split(',').map(t => t.trim()).filter(Boolean);
  }
}
