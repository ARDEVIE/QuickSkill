import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface Category {
  id: number;
  name: string;
  slug: string;
}

export interface Author {
  id: number;
  username: string;
  first_name?: string;
  last_name?: string;
  avatar: string | null;
  telegram_url?: string;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  cover: string | null;
  category: Category;
  author: Author;
  is_published: boolean;
  created_at: string;
}

export type MaterialType = 'pdf' | 'video_link' | 'link' | 'text';

export interface Material {
  id: number;
  course: number;
  lesson: number | null;
  title: string;
  type: MaterialType;
  file: string | null;
  url: string | null;
  content: string | null;
  order: number;
  created_at: string;
}

export interface Lesson {
  id: number;
  course: number;
  title: string;
  description: string;
  order: number;
  materials: Material[];
  created_at: string;
}

export interface Rating {
  id: number;
  course: number;
  user: Author;
  score: number;
  comment: string;
  created_at: string;
}

export interface CourseDetail extends Course {
  updated_at: string;
  lessons: Lesson[];
  materials: Material[];
  ratings: Rating[];
  average_rating: number | null;
  ratings_count: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({
  providedIn: 'root'
})
export class CourseService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getCategories(): Observable<Category[]> {
    // Assuming unpaginated or we just want results
    // Wait, let's assume it's paginated since DRF default pagination is enabled, but categories might just use it
    return this.http.get<Category[] | PaginatedResponse<Category>>(`${this.apiUrl}/categories/`) as any;
  }

  getCourses(params?: any): Observable<PaginatedResponse<Course>> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key]) {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }
    return this.http.get<PaginatedResponse<Course>>(`${this.apiUrl}/courses/`, { params: httpParams });
  }

  getCourse(id: number): Observable<CourseDetail> {
    return this.http.get<CourseDetail>(`${this.apiUrl}/courses/${id}/`);
  }

  createCourse(courseData: FormData): Observable<Course> {
    return this.http.post<Course>(`${this.apiUrl}/courses/`, courseData);
  }

  updateCourse(id: number, courseData: Partial<Course> | FormData): Observable<Course> {
    return this.http.patch<Course>(`${this.apiUrl}/courses/${id}/`, courseData);
  }

  toggleFavorite(id: number): Observable<{ favorited: boolean }> {
    return this.http.post<{ favorited: boolean }>(`${this.apiUrl}/courses/${id}/favorite/`, {});
  }

  addMaterial(courseId: number, materialData: FormData | any): Observable<Material> {
    return this.http.post<Material>(`${this.apiUrl}/courses/${courseId}/materials/`, materialData);
  }

  rateCourse(courseId: number, ratingData: { score: number, comment: string }): Observable<Rating> {
    return this.http.post<Rating>(`${this.apiUrl}/courses/${courseId}/ratings/`, ratingData);
  }

  getFavoriteCourses(): Observable<PaginatedResponse<Course> | Course[]> {
    return this.http.get<PaginatedResponse<Course> | Course[]>(`${this.apiUrl}/courses/favorites/`);
  }

  createLesson(courseId: number, data: { title: string, description?: string, order?: number }): Observable<Lesson> {
    return this.http.post<Lesson>(`${this.apiUrl}/courses/${courseId}/lessons/`, data);
  }

  updateLesson(lessonId: number, data: Partial<Pick<Lesson, 'title' | 'description' | 'order'>>): Observable<Lesson> {
    return this.http.patch<Lesson>(`${this.apiUrl}/lessons/${lessonId}/`, data);
  }

  deleteLesson(lessonId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/lessons/${lessonId}/`);
  }

  addMaterialToLesson(lessonId: number, materialData: FormData | any): Observable<Material> {
    return this.http.post<Material>(`${this.apiUrl}/lessons/${lessonId}/materials/`, materialData);
  }
}
