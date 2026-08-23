import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  avatar: string | null;
  role: string;
  bio?: string;
  telegram_username?: string;
  telegram_url?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    // Optionally load user on initialization if tokens exist
  }

  public get accessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  public get refreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  login(credentials: { email: string; password: string }): Observable<AuthTokens> {
    return this.http.post<AuthTokens>(`${this.apiUrl}/auth/login/`, credentials).pipe(
      tap(tokens => this.storeTokens(tokens))
    );
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register/`, userData);
  }

  requestPasswordReset(email: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/password-reset/`, { email });
  }

  resetPassword(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/password-reset-confirm/`, data);
  }

  logout(): void {
    const refresh = this.refreshToken;
    if (refresh) {
      this.http.post(`${this.apiUrl}/auth/logout/`, { refresh }).subscribe({
        next: () => this.clearAuth(),
        error: () => this.clearAuth()
      });
    } else {
      this.clearAuth();
    }
  }

  refreshTokens(): Observable<AuthTokens> {
    const refresh = this.refreshToken;
    if (!refresh) {
      return throwError(() => new Error('No refresh token available'));
    }
    return this.http.post<AuthTokens>(`${this.apiUrl}/auth/refresh/`, { refresh }).pipe(
      tap(tokens => this.storeTokens(tokens)),
      catchError(error => {
        this.clearAuth();
        return throwError(() => error);
      })
    );
  }

  fetchCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/users/me/`).pipe(
      tap(user => this.currentUserSubject.next(user))
    );
  }

  updateProfile(data: Partial<User> | FormData): Observable<User> {
    return this.http.patch<User>(`${this.apiUrl}/users/me/`, data).pipe(
      tap(user => this.currentUserSubject.next(user))
    );
  }

  private storeTokens(tokens: AuthTokens): void {
    if (tokens.access) localStorage.setItem('access_token', tokens.access);
    if (tokens.refresh) localStorage.setItem('refresh_token', tokens.refresh);
  }

  public clearAuth(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUserSubject.next(null);
  }
}
