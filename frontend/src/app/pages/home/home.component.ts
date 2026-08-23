import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CourseService, Course, Category } from 'src/app/core/services/course.service';

interface UICourse extends Course {
  rating: string;
  students: string;
  lessons: string;
  color: string;
  icon: string;
  authorName: string;
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  categories: Category[] = [];
  courses: UICourse[] = [];
  searchQuery: string = '';

  private colors = ['#DCEAFF', '#FFF0E4', '#E5F7F1', '#EAE7FF', '#E8F0FF', '#FFF4D9', '#E7F5FF', '#F2E9FF'];
  private icons = ['</>', '✦', 'Py', '↗', 'A', 'F', '{ }', '★'];

  constructor(private courseService: CourseService, private router: Router) {}

  ngOnInit(): void {
    this.courseService.getCategories().subscribe(res => {
      const cats = (res as any).results || res;
      this.categories = cats.slice(0, 10);
    });

    this.courseService.getCourses().subscribe(res => {
      const crs = res.results || [];
      this.courses = crs.slice(0, 10).map((c: any, i: number) => ({
        ...c,
        authorName: c.author ? (c.author.first_name || c.author.username) : 'Неизвестно',
        rating: c.average_rating ? c.average_rating.toString() : '0',
        students: '100',
        lessons: '10 уроков',
        color: this.colors[i % this.colors.length],
        icon: this.icons[i % this.icons.length]
      }));
    });
  }

  onSearch(): void {
    if (this.searchQuery.trim()) {
      this.router.navigate(['/courses'], { queryParams: { search: this.searchQuery.trim() } });
    }
  }

  goToCategory(slug: string): void {
    this.router.navigate(['/courses'], { queryParams: { category: slug } });
  }

  goToCourse(id: number): void {
    this.router.navigate(['/courses', id]);
  }
}