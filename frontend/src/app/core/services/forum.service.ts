import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { Author, Category, PaginatedResponse } from './course.service';

export interface Question {
  id: number;
  title: string;
  slug: string;
  content: string;
  category: Category;
  author: Author;
  created_at: string;
  views: number;
  comments_count: number;
  accepted_comment: number | null;
  media_file?: string | null;
}

export interface QuestionDetail extends Question {
  comments: Comment[]; // actually, DRF returns comments via nested? Wait, QuestionDetailSerializer has comments? Let me check. The comments view is separate or nested? Ah, the view has an action `@action comments` which returns comments paginated. But maybe the detail returns some comments? We will fetch them separately anyway.
}

export interface Comment {
  id: number;
  question: number;
  user: Author;
  content: string;
  created_at: string;
  updated_at: string;
  media_file?: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class ForumService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getQuestions(params?: any): Observable<PaginatedResponse<Question>> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key]) httpParams = httpParams.set(key, params[key]);
      });
    }
    return this.http.get<PaginatedResponse<Question>>(`${this.apiUrl}/questions/`, { params: httpParams });
  }

  getQuestion(slug: string): Observable<Question> {
    return this.http.get<Question>(`${this.apiUrl}/questions/${slug}/`);
  }

  createQuestion(data: FormData | any): Observable<Question> {
    return this.http.post<Question>(`${this.apiUrl}/questions/`, data);
  }

  updateQuestion(slug: string, data: FormData | any): Observable<Question> {
    return this.http.patch<Question>(`${this.apiUrl}/questions/${slug}/`, data);
  }

  deleteQuestion(slug: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/questions/${slug}/`);
  }

  getComments(slug: string): Observable<Comment[]> {
    // using unpaginated or paginated, we'll assume paginated but handle array or PaginatedResponse
    return this.http.get<Comment[]>(`${this.apiUrl}/questions/${slug}/comments/`) as any;
  }

  addComment(slug: string, formData: FormData | any): Observable<Comment> {
    return this.http.post<Comment>(`${this.apiUrl}/questions/${slug}/comments/`, formData);
  }

  acceptAnswer(slug: string, commentId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/questions/${slug}/accept_answer/`, { comment_id: commentId });
  }

  toggleFavorite(slug: string): Observable<{ favorited: boolean }> {
    return this.http.post<{ favorited: boolean }>(`${this.apiUrl}/questions/${slug}/favorite/`, {});
  }

  getFavoriteQuestions(): Observable<PaginatedResponse<Question> | Question[]> {
    return this.http.get<PaginatedResponse<Question> | Question[]>(`${this.apiUrl}/questions/favorites/`);
  }
}
