import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HomeComponent } from './pages/home/home.component';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';
import { CoursesComponent } from './pages/courses/courses.component';
import { CreateCourseComponent } from './pages/create-course/create-course.component';
import { CourseDetailsComponent } from './pages/course-details/course-details.component';
import { CourseEditorComponent } from './pages/course-editor/course-editor.component';
import { CoursePlayerComponent } from './pages/course-player/course-player.component';
import { ProfileComponent } from './pages/profile/profile.component';
import { ForgotPasswordComponent } from './pages/forgot-password/forgot-password.component';
import { ResetPasswordComponent } from './pages/reset-password/reset-password.component';
import { ForumListComponent } from './pages/forum-list/forum-list.component';
import { QuestionDetailsComponent } from './pages/question-details/question-details.component';
import { CreateQuestionComponent } from './pages/create-question/create-question.component';
import { PublicProfileComponent } from './pages/public-profile/public-profile.component';
import { FavoritesComponent } from './pages/favorites/favorites.component';
import { SubjectListComponent } from './pages/subject-list/subject-list.component';
import { SubjectDetailComponent } from './pages/subject-detail/subject-detail.component';
import { ShareMaterialComponent } from './pages/share-material/share-material.component';

const routes: Routes = [
  {
    path: '',
    component: HomeComponent
  },
  {
    path: 'login',
    component: LoginComponent
  },

  {
    path: 'register',
    component: RegisterComponent
  },

  {
    path: 'courses',
    component: CoursesComponent
  },
  {
    path: 'create-course',
    component: CreateCourseComponent
  },

  {
    path: 'forum',
    component: ForumListComponent
  },
  {
    path: 'forum/ask',
    component: CreateQuestionComponent
  },
  {
    path: 'forum/:slug',
    component: QuestionDetailsComponent
  },
  {
    path: 'courses/:id/edit',
    component: CourseEditorComponent
  },
  {
    path: 'courses/:id/learn',
    component: CoursePlayerComponent
  },
  {
    path: 'courses/:id',
    component: CourseDetailsComponent
  },
  {
    path: 'profile',
    component: ProfileComponent
  },
  {
    path: 'favorites',
    component: FavoritesComponent
  },
  {
    path: 'subjects',
    component: SubjectListComponent
  },
  {
    path: 'subjects/:id',
    component: SubjectDetailComponent
  },
  {
    path: 'share-material',
    component: ShareMaterialComponent
  },
  {
    path: 'public-profile/:username',
    component: PublicProfileComponent
  },
  {
    path: 'forgot-password',
    component: ForgotPasswordComponent
  },
  {
    path: 'reset-password/:uid/:token',
    component: ResetPasswordComponent
  }
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes)
  ],
  exports: [
    RouterModule
  ]
})
export class AppRoutingModule {}