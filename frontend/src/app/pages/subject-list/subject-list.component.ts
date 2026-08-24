import { Component, OnInit } from '@angular/core';
import { Category } from 'src/app/core/services/course.service';
import { SubjectService } from 'src/app/core/services/subject.service';
import { AuthService, User } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-subject-list',
  templateUrl: './subject-list.component.html',
  styleUrls: ['./subject-list.component.scss']
})
export class SubjectListComponent implements OnInit {
  subjects: Category[] = [];
  isLoading = true;
  currentUser: User | null = null;

  constructor(private subjectService: SubjectService, private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    this.subjectService.getSubjects().subscribe({
      next: (res) => {
        this.subjects = (res as any).results || res;
        this.isLoading = false;
      },
      error: () => this.isLoading = false
    });
  }
}
