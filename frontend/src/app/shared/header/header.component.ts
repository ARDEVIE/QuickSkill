import { Component, OnInit } from '@angular/core';
import { AuthService, User } from 'src/app/core/services/auth.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {
  currentUser$: Observable<User | null>;

  constructor(private authService: AuthService) {
    this.currentUser$ = this.authService.currentUser$;
  }

  ngOnInit(): void {
    if (this.authService.accessToken) {
      this.authService.fetchCurrentUser().subscribe({
        error: () => this.authService.clearAuth()
      });
    }
  }

  logout(): void {
    this.authService.logout();
  }
}
