import { Component, OnInit } from '@angular/core';
import { CourseService, Course, Category } from 'src/app/core/services/course.service';

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
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  categories: Category[] = [];
  courses: UICourse[] = [];

  private colors = ['#DCEAFF', '#FFF0E4', '#E5F7F1', '#EAE7FF', '#E8F0FF', '#FFF4D9', '#E7F5FF', '#F2E9FF'];
  private icons = ['</>', '✦', 'Py', '↗', 'A', 'F', '{ }', '★'];

  constructor(private courseService: CourseService) {}

  ngOnInit(): void {
    this.courseService.getCategories().subscribe(res => {
      const cats = (res as any).results || res;
      this.categories = cats.slice(0, 6); // Just show top 6
    });

    this.courseService.getCourses().subscribe(res => {
      const crs = res.results || [];
      this.courses = crs.slice(0, 4).map((c: Course, i: number) => ({
        ...c,
        authorName: c.author ? (c.author.first_name || c.author.username) : 'Неизвестно',
        level: 'Начальный',
        rating: '4.8',
        students: '100',
        lessons: '10 уроков',
        color: this.colors[i % this.colors.length],
        icon: this.icons[i % this.icons.length]
      }));
    });
  }
}