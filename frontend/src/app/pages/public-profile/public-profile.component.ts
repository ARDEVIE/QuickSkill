import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService, PublicUser } from 'src/app/core/services/auth.service';
import { CourseService, Course } from 'src/app/core/services/course.service';

@Component({
  selector: 'app-public-profile',
  templateUrl: './public-profile.component.html',
  styleUrls: ['./public-profile.component.scss']
})
export class PublicProfileComponent implements OnInit {
  user: PublicUser | null = null;
  courses: Course[] = [];
  isLoading = true;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private courseService: CourseService
  ) {}

  ngOnInit(): void {
    const username = this.route.snapshot.paramMap.get('username');
    if (!username) {
      this.router.navigate(['/']);
      return;
    }

    this.authService.getPublicProfile(username).subscribe({
      next: (u) => {
        this.user = u;
        // Fetch courses by author if needed, or if backend includes it, just use it.
        // QuickSkill backend doesn't necessarily include courses in public profile unless specified,
        // so let's try to query courses by author if possible.
        // Assuming courses endpoint accepts author=username or author=id.
        this.courseService.getCourses({ author: u.id, public_only: 'true' }).subscribe(res => {
          this.courses = res.results;
          this.isLoading = false;
        });
      },
      error: () => {
        this.router.navigate(['/']);
      }
    });
  }
}
