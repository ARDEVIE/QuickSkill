import { Component, OnInit } from '@angular/core';
import { CourseService, Course } from 'src/app/core/services/course.service';
import { ForumService, Question } from 'src/app/core/services/forum.service';

@Component({
  selector: 'app-favorites',
  templateUrl: './favorites.component.html',
  styleUrls: ['./favorites.component.scss']
})
export class FavoritesComponent implements OnInit {
  courses: Course[] = [];
  questions: Question[] = [];
  isLoadingCourses = true;
  isLoadingQuestions = true;

  constructor(
    private courseService: CourseService,
    private forumService: ForumService
  ) {}

  ngOnInit(): void {
    this.courseService.getFavoriteCourses().subscribe({
      next: (res) => {
        this.courses = (res as any).results || res;
        this.isLoadingCourses = false;
      },
      error: () => { this.isLoadingCourses = false; }
    });

    this.forumService.getFavoriteQuestions().subscribe({
      next: (res) => {
        this.questions = (res as any).results || res;
        this.isLoadingQuestions = false;
      },
      error: () => { this.isLoadingQuestions = false; }
    });
  }
}
