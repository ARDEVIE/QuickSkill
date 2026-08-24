import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HeaderComponent } from './shared/header/header.component';
import { FooterComponent } from './shared/footer/footer.component';
import { HomeComponent } from './pages/home/home.component';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';
import { CoursesComponent } from './pages/courses/courses.component';
import { CreateCourseComponent } from './pages/create-course/create-course.component';
import { CourseDetailsComponent } from './pages/course-details/course-details.component';
import { JwtInterceptor } from './core/interceptors/jwt.interceptor';
import { ProfileComponent } from './pages/profile/profile.component';
import { ForgotPasswordComponent } from './pages/forgot-password/forgot-password.component';
import { ResetPasswordComponent } from './pages/reset-password/reset-password.component';
import { CourseEditorComponent } from './pages/course-editor/course-editor.component';
import { CoursePlayerComponent } from './pages/course-player/course-player.component';
import { ForumListComponent } from './pages/forum-list/forum-list.component';
import { QuestionDetailsComponent } from './pages/question-details/question-details.component';
import { CreateQuestionComponent } from './pages/create-question/create-question.component';
import { PublicProfileComponent } from './pages/public-profile/public-profile.component';
import { FavoritesComponent } from './pages/favorites/favorites.component';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    FooterComponent,
    HomeComponent,
    LoginComponent,
    RegisterComponent,
    CoursesComponent,
    CreateCourseComponent,
    CourseDetailsComponent,
    ProfileComponent,
    ForgotPasswordComponent,
    ResetPasswordComponent,
    CourseEditorComponent,
    CoursePlayerComponent,
    ForumListComponent,
    QuestionDetailsComponent,
    CreateQuestionComponent,
    PublicProfileComponent,
    FavoritesComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
