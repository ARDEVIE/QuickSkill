import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { Author, Category, PaginatedResponse } from './course.service';

export interface SubjectDetail extends Category {
  description: string;
  students_count: number;
  materials_count: number;
  guides_count: number;
  questions_count: number;
  is_following: boolean;
}

export type ResourceType = 'pdf' | 'notes' | 'cheatsheet' | 'past_paper' | 'link' | 'video';

export interface Resource {
  id: number;
  category: Category;
  author: Author;
  title: string;
  type: ResourceType;
  url: string | null;
  file: string | null;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class SubjectService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getSubjects(): Observable<PaginatedResponse<Category> | Category[]> {
    return this.http.get<PaginatedResponse<Category> | Category[]>(`${this.apiUrl}/categories/`);
  }

  getSubject(id: number): Observable<SubjectDetail> {
    return this.http.get<SubjectDetail>(`${this.apiUrl}/categories/${id}/`);
  }

  toggleFollow(id: number): Observable<{ following: boolean }> {
    return this.http.post<{ following: boolean }>(`${this.apiUrl}/categories/${id}/follow/`, {});
  }

  getResources(params?: any): Observable<PaginatedResponse<Resource> | Resource[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key]) httpParams = httpParams.set(key, params[key]);
      });
    }
    return this.http.get<PaginatedResponse<Resource> | Resource[]>(`${this.apiUrl}/resources/`, { params: httpParams });
  }

  createResource(data: FormData): Observable<Resource> {
    return this.http.post<Resource>(`${this.apiUrl}/resources/`, data);
  }

  deleteResource(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/resources/${id}/`);
  }
}
