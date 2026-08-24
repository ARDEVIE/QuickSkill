import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CourseService, Course, Category } from 'src/app/core/services/course.service';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

interface UICourse extends Course {
  color: string;
  icon: string;
  authorName: string;
}

@Component({
  selector: 'app-courses',
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.scss']
})
export class CoursesComponent implements OnInit {
  courses: UICourse[] = [];
  categories: Category[] = [];
  activeCategories: (string | number)[] = [];
  minRating: number | null = null;
  currentSort: string | null = null;
  totalCourses = 0;
  
  searchQuery = '';
  private searchSubject = new Subject<string>();

  private colors = ['#DCEAFF', '#FFF0E4', '#E5F7F1', '#EAE7FF', '#E8F0FF', '#FFF4D9', '#E7F5FF', '#F2E9FF'];
  private icons = ['</>', '✦', 'Py', '↗', 'A', 'F', '{ }', '★'];

  constructor(private courseService: CourseService, private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.searchQuery = this.route.snapshot.queryParamMap.get('search') || '';

    this.fetchCategories();

    this.route.queryParams.subscribe(params => {
      if (params['search']) {
        this.searchQuery = params['search'];
      }
      if (params['category']) {
        this.activeCategories = [params['category']];
      }
      if (params['categories']) {
        this.activeCategories = params['categories'].split(',').map((c: string) => Number(c) || c);
      }
      if (params['min_rating']) {
        this.minRating = Number(params['min_rating']);
      }
      this.fetchCourses();
    });

    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(query => {
      this.searchQuery = query;
      this.fetchCourses();
    });
  }

  fetchCategories(): void {
    this.courseService.getCategories().subscribe(res => {
      this.categories = (res as any).results || res; // handle both paginated and list
    });
  }

  fetchCourses(): void {
    const params: any = {};
    if (this.searchQuery) {
      params.search = this.searchQuery;
    }
    if (this.activeCategories.length > 0) {
      params.categories = this.activeCategories.join(',');
    }
    if (this.minRating !== null) {
      params.min_rating = this.minRating;
    }
    if (this.currentSort) {
      params.sort = this.currentSort;
    }

    this.courseService.getCourses(params).subscribe(res => {
      this.totalCourses = res.count;
      this.courses = res.results.map((c, i) => this.mapToUICourse(c, i));
    });
  }

  toggleCategory(categoryId: string | number): void {
    const index = this.activeCategories.indexOf(categoryId);
    if (index > -1) {
      this.activeCategories.splice(index, 1);
    } else {
      this.activeCategories.push(categoryId);
    }
    this.fetchCourses();
  }

  setRatingFilter(rating: number | null): void {
    this.minRating = rating;
    this.fetchCourses();
  }

  setSort(sort: string | null): void {
    this.currentSort = sort;
    this.fetchCourses();
  }

  onSearch(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.searchSubject.next(target.value);
  }

  private mapToUICourse(course: any, index: number): UICourse {
    return {
      ...course,
      authorName: course.author ? (course.author.first_name || course.author.username) : 'Неизвестно',
      color: this.colors[index % this.colors.length],
      icon: this.icons[index % this.icons.length]
    };
  }
}