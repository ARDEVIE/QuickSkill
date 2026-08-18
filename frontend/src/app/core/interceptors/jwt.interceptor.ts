import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, filter, switchMap, take } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Injectable()
export class JwtInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);

  constructor(private authService: AuthService, private router: Router) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    let authReq = request;
    const token = this.authService.accessToken;

    if (token) {
      authReq = this.addTokenHeader(request, token);
    }

    return next.handle(authReq).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401 && !authReq.url.includes('auth/login')) {
          return this.handle401Error(authReq, next);
        }
        return throwError(() => error);
      })
    );
  }

  private handle401Error(request: HttpRequest<any>, next: HttpHandler) {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);

      const token = this.authService.refreshToken;
      if (token) {
        return this.authService.refreshTokens().pipe(
          switchMap((tokens: any) => {
            this.isRefreshing = false;
            this.refreshTokenSubject.next(tokens.access);
            return next.handle(this.addTokenHeader(request, tokens.access));
          }),
          catchError((err) => {
            this.isRefreshing = false;
            this.authService.clearAuth();
            this.router.navigate(['/login']);
            return throwError(() => err);
          })
        );
      } else {
        this.isRefreshing = false;
        this.authService.clearAuth();
        this.router.navigate(['/login']);
        return throwError(() => new Error('No refresh token'));
      }
    } else {
      // Race condition protection: wait until isRefreshing becomes false
      return this.refreshTokenSubject.pipe(
        filter(token => token !== null),
        take(1),
        switchMap((jwt) => {
          return next.handle(this.addTokenHeader(request, jwt));
        })
      );
    }
  }

  private addTokenHeader(request: HttpRequest<any>, token: string) {
    return request.clone({
      headers: request.headers.set('Authorization', `Bearer ${token}`)
    });
  }
}
