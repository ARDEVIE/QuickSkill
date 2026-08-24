import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HomeComponent } from './pages/home/home.component';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';
import { CoursesComponent } from './pages/courses/courses.component';
import { CreateCourseComponent } from './pages/create-course/create-course.component';
import { CourseDetailsComponent } from './pages/course-details/course-details.component';
import { EditCourseComponent } from './pages/edit-course/edit-course.component';
import { ProfileComponent } from './pages/profile/profile.component';
import { ForgotPasswordComponent } from './pages/forgot-password/forgot-password.component';
import { ResetPasswordComponent } from './pages/reset-password/reset-password.component';
import { ForumListComponent } from './pages/forum-list/forum-list.component';
import { QuestionDetailsComponent } from './pages/question-details/question-details.component';
import { CreateQuestionComponent } from './pages/create-question/create-question.component';
import { PublicProfileComponent } from './pages/public-profile/public-profile.component';
import { InfoPageComponent } from './pages/info-page/info-page.component';
import { FAQ_PAGE, SUPPORT_PAGE, TERMS_PAGE } from './pages/info-page/info-page.content';
import { FavoritesComponent } from './pages/favorites/favorites.component';

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
    component: EditCourseComponent
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
    path: 'public-profile/:username',
    component: PublicProfileComponent
  },
  {
    path: 'favorites',
    component: FavoritesComponent
  },
  {
    path: 'forgot-password',
    component: ForgotPasswordComponent
  },
  {
    path: 'reset-password/:uid/:token',
    component: ResetPasswordComponent
  },

  {
    path: 'faq',
    component: InfoPageComponent,
    data: { info: FAQ_PAGE }
  },
  {
    path: 'support',
    component: InfoPageComponent,
    data: { info: SUPPORT_PAGE }
  },
  {
    path: 'terms',
    component: InfoPageComponent,
    data: { info: TERMS_PAGE }
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