import { Component, HostListener, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { forkJoin, of } from 'rxjs';
import { CourseService, Course, Category } from 'src/app/core/services/course.service';
import { SubjectService, Resource } from 'src/app/core/services/subject.service';
import { ForumService, Question } from 'src/app/core/services/forum.service';
import { AuthService, User } from 'src/app/core/services/auth.service';

interface UICourse extends Course {
  authorName: string;
  color: string;
  icon: string;
}

interface SearchResults {
  subjects: Category[];
  courses: Course[];
  materials: Resource[];
  questions: Question[];
}

const MIN_SEARCH_LENGTH = 2;

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  currentUser: User | null = null;

  // Anonymous homepage (unchanged behavior)
  categories: Category[] = [];
  courses: UICourse[] = [];

  // Logged-in dashboard
  allSubjects: Category[] = [];
  mySubjects: Category[] = [];
  continueLearning: UICourse[] = [];
  forYou: UICourse[] = [];
  popularCourses: UICourse[] = [];
  popularQuestions: Question[] = [];
  recentQuestions: Question[] = [];
  newCourses: UICourse[] = [];
  newMaterials: Resource[] = [];
  isLoadingDashboard = true;

  // Search (used in both states)
  searchQuery = '';
  searchResults: SearchResults | null = null;
  isSearching = false;
  showResults = false;
  private searchInput$ = new Subject<string>();

  private colors = ['#DCEAFF', '#FFF0E4', '#E5F7F1', '#EAE7FF', '#E8F0FF', '#FFF4D9', '#E7F5FF', '#F2E9FF'];
  private icons = ['</>', '✦', 'Py', '↗', 'A', 'F', '{ }', '★'];

  constructor(
    private courseService: CourseService,
    private subjectService: SubjectService,
    private forumService: ForumService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      const wasLoggedIn = !!this.currentUser;
      this.currentUser = user;
      if (user && !wasLoggedIn) {
        this.loadDashboard();
      } else if (!user) {
        this.loadAnonymousHome();
      }
    });

    this.searchInput$.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(query => {
        if (query.trim().length < MIN_SEARCH_LENGTH) return of(null);
        this.isSearching = true;
        return forkJoin({
          courses: this.courseService.getCourses({ search: query, public_only: 'true' }),
          materials: this.subjectService.getResources({ search: query }),
          questions: this.forumService.getQuestions({ search: query })
        });
      })
    ).subscribe(res => {
      this.isSearching = false;
      if (!res) { this.searchResults = null; return; }
      const q = this.searchQuery.trim().toLowerCase();
      this.searchResults = {
        subjects: this.allSubjects.filter(s => s.name.toLowerCase().includes(q)).slice(0, 4),
        courses: ((res.courses as any).results || []).slice(0, 4),
        materials: ((res.materials as any).results || []).slice(0, 4),
        questions: ((res.questions as any).results || []).slice(0, 4)
      };
    });
  }

  private toUICourse(c: Course, i: number): UICourse {
    return {
      ...c,
      authorName: c.author ? (c.author.first_name || c.author.username) : 'Неизвестно',
      color: this.colors[i % this.colors.length],
      icon: this.icons[i % this.icons.length]
    } as UICourse;
  }

  private loadAnonymousHome(): void {
    this.courseService.getCategories().subscribe(res => {
      const cats = (res as any).results || res;
      this.categories = cats.slice(0, 10);
      this.allSubjects = cats;
    });

    this.courseService.getCourses().subscribe(res => {
      const crs = res.results || [];
      this.courses = crs.slice(0, 10).map((c, i) => this.toUICourse(c, i));
    });
  }

  private loadDashboard(): void {
    this.isLoadingDashboard = true;

    this.courseService.getCategories().subscribe(res => {
      this.allSubjects = (res as any).results || res;
    });

    this.subjectService.getSubjects({ following: 'true' }).subscribe(res => {
      this.mySubjects = ((res as any).results || res).slice(0, 8);

      // "For You": courses in followed subjects, best-rated first. Only
      // meaningful once the student follows something — otherwise it would
      // just duplicate "Popular in KBTU".
      if (this.mySubjects.length > 0) {
        const categoryIds = this.mySubjects.map(s => s.id).join(',');
        this.courseService.getCourses({ categories: categoryIds, sort: 'rating_desc', public_only: 'true' }).subscribe(res2 => {
          this.forYou = (res2.results || []).slice(0, 4).map((c, i) => this.toUICourse(c, i));
        });
      }
    });

    this.courseService.getCourses({ filter: 'in_progress' }).subscribe(res => {
      this.continueLearning = (res.results || []).map((c, i) => this.toUICourse(c, i));
      this.isLoadingDashboard = false;
    });

    this.courseService.getCourses({ sort: 'rating_desc', public_only: 'true' }).subscribe(res => {
      this.popularCourses = (res.results || []).slice(0, 4).map((c, i) => this.toUICourse(c, i));
    });

    this.forumService.getQuestions({ filter: 'popular' }).subscribe(res => {
      this.popularQuestions = (res.results || []).slice(0, 4);
    });

    this.forumService.getQuestions({}).subscribe(res => {
      this.recentQuestions = (res.results || []).slice(0, 5);
    });

    this.courseService.getCourses({ public_only: 'true' }).subscribe(res => {
      this.newCourses = (res.results || []).slice(0, 6).map((c, i) => this.toUICourse(c, i));
    });

    this.subjectService.getResources({}).subscribe(res => {
      this.newMaterials = ((res as any).results || res).slice(0, 4);
    });
  }

  // ---------- Search ----------

  onSearchInput(): void {
    this.showResults = true;
    this.searchInput$.next(this.searchQuery);
  }

  onSearchFocus(): void {
    if (this.searchQuery.trim().length >= MIN_SEARCH_LENGTH) this.showResults = true;
  }

  onSearch(): void {
    this.showResults = false;
    if (this.searchQuery.trim()) {
      this.router.navigate(['/courses'], { queryParams: { search: this.searchQuery.trim() } });
    }
  }

  closeResults(): void {
    this.showResults = false;
  }

  onSearchBlur(event: FocusEvent): void {
    const wrapper = event.currentTarget as HTMLElement;
    const nextFocus = event.relatedTarget as HTMLElement | null;
    if (!nextFocus || !wrapper.contains(nextFocus)) {
      this.showResults = false;
    }
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.showResults = false;
  }

  goToCategory(slug: string): void {
    this.router.navigate(['/courses'], { queryParams: { category: slug } });
  }

  goToCourse(id: number): void {
    this.router.navigate(['/courses', id]);
  }
}
