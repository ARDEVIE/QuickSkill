import { Component, OnInit } from '@angular/core';
import { CourseService, Course, Category } from 'src/app/core/services/course.service';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

interface UICourse extends Course {
  level: string;
  rating: string;
  students: string;
  lessons: string;
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
  activeCategory: number | null = null;
  totalCourses = 0;
  
  searchQuery = '';
  private searchSubject = new Subject<string>();

  private colors = ['#DCEAFF', '#FFF0E4', '#E5F7F1', '#EAE7FF', '#E8F0FF', '#FFF4D9', '#E7F5FF', '#F2E9FF'];
  private icons = ['</>', '✦', 'Py', '↗', 'A', 'F', '{ }', '★'];

  constructor(private courseService: CourseService) {}

  ngOnInit(): void {
    this.fetchCategories();
    this.fetchCourses();

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
    if (this.activeCategory) {
      params.category = this.activeCategory;
    }

    this.courseService.getCourses(params).subscribe(res => {
      this.totalCourses = res.count;
      this.courses = res.results.map((c, i) => this.mapToUICourse(c, i));
    });
  }

  setCategory(categoryId: number | null): void {
    this.activeCategory = categoryId;
    this.fetchCourses();
  }

  onSearch(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.searchSubject.next(target.value);
  }

  private mapToUICourse(course: Course, index: number): UICourse {
    return {
      ...course,
      authorName: course.author ? (course.author.first_name || course.author.username) : 'Неизвестно',
      level: 'Начальный', // Placeholder as backend doesn't have level
      rating: '4.8', // Placeholder, we can fetch later if needed
      students: '100', // Placeholder
      lessons: '10 уроков', // Placeholder
      color: this.colors[index % this.colors.length],
      icon: this.icons[index % this.icons.length]
    };
  }
}