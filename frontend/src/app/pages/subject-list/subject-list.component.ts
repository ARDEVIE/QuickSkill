import { Component, OnInit } from '@angular/core';
import { Category } from 'src/app/core/services/course.service';
import { SubjectService } from 'src/app/core/services/subject.service';

@Component({
  selector: 'app-subject-list',
  templateUrl: './subject-list.component.html',
  styleUrls: ['./subject-list.component.scss']
})
export class SubjectListComponent implements OnInit {
  subjects: Category[] = [];
  isLoading = true;

  constructor(private subjectService: SubjectService) {}

  ngOnInit(): void {
    this.subjectService.getSubjects().subscribe({
      next: (res) => {
        this.subjects = (res as any).results || res;
        this.isLoading = false;
      },
      error: () => this.isLoading = false
    });
  }
}
