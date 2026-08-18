import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService, User } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
  user: User | null = null;
  isLoading = true;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    if (!this.authService.accessToken) {
      this.router.navigate(['/login']);
      return;
    }

    this.authService.fetchCurrentUser().subscribe({
      next: (u) => {
        this.user = u;
        this.isLoading = false;
      },
      error: () => {
        this.authService.clearAuth();
        this.router.navigate(['/login']);
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }
}
