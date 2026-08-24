import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/core/services/auth.service';
import { ForumService, Question } from 'src/app/core/services/forum.service';

@Component({
  selector: 'app-favorites',
  templateUrl: './favorites.component.html',
  styleUrls: ['./favorites.component.scss']
})
export class FavoritesComponent implements OnInit {
  courses: any[] = [];
  questions: Question[] = [];
  isLoading = true;

  constructor(
    private authService: AuthService,
    private forumService: ForumService,
    private router: Router
  ) {}

  ngOnInit(): void {
    if (!this.authService.accessToken) {
      this.router.navigate(['/login']);
      return;
    }

    this.authService.getFavorites().subscribe(res => {
      this.courses = (res as any).results || res;
      this.isLoading = false;
    });

    this.forumService.getFavoriteQuestions().subscribe(res => {
      this.questions = (res as any).results || (res as any);
    });
  }
}
