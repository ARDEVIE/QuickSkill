import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CourseService, Course, Category } from 'src/app/core/services/course.service';

interface UICourse extends Course {
  color: string;
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
  heroSearchQuery = '';

  private colors = ['#DCEAFF', '#FFF0E4', '#E5F7F1', '#EAE7FF', '#E8F0FF', '#FFF4D9', '#E7F5FF', '#F2E9FF'];

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
        color: this.colors[i % this.colors.length]
      }));
    });
  }

  onHeroSearch(): void {
    const query = this.heroSearchQuery.trim();
    this.router.navigate(['/courses'], query ? { queryParams: { search: query } } : {});
  }

  goToCategory(slug: string): void {
    this.router.navigate(['/courses'], { queryParams: { category: slug } });
  }

  goToCourse(id: number): void {
    this.router.navigate(['/courses', id]);
  }
}