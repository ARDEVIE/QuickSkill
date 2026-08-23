import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ForumService, Question, Comment } from 'src/app/core/services/forum.service';
import { AuthService, User } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-question-details',
  templateUrl: './question-details.component.html',
  styleUrls: ['./question-details.component.scss']
})
export class QuestionDetailsComponent implements OnInit {
  question: Question | null = null;
  comments: Comment[] = [];
  slug = '';
  
  isLoggedIn = false;
  isAuthor = false;
  currentUser: User | null = null;

  commentForm: FormGroup;
  isSubmitting = false;
  commentError: string | null = null;
  acceptError: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private forumService: ForumService,
    private authService: AuthService,
    private fb: FormBuilder
  ) {
    this.commentForm = this.fb.group({
      content: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    this.slug = this.route.snapshot.paramMap.get('slug') || '';
    
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      this.isLoggedIn = !!user;
      this.checkAuthor();
    });

    if (this.slug) {
      this.loadQuestion();
      this.loadComments();
    }
  }

  loadQuestion(): void {
    this.forumService.getQuestion(this.slug).subscribe(res => {
      this.question = res;
      this.checkAuthor();
    });
  }

  loadComments(): void {
    this.forumService.getComments(this.slug).subscribe(res => {
      this.comments = (res as any).results || res;
    });
  }

  checkAuthor(): void {
    if (this.question && this.currentUser) {
      this.isAuthor = this.question.author.id === this.currentUser.id;
    }
  }

  onAddComment(): void {
    if (this.commentForm.invalid) return;

    this.isSubmitting = true;
    this.commentError = null;
    this.forumService.addComment(this.slug, this.commentForm.value).subscribe({
      next: (comment) => {
        this.comments.push(comment);
        if (this.question) this.question.comments_count++;
        this.commentForm.reset();
        this.isSubmitting = false;
      },
      error: () => {
        this.isSubmitting = false;
        this.commentError = 'Ошибка при отправке ответа';
      }
    });
  }

  acceptAnswer(commentId: number): void {
    if (!this.question) return;
    this.acceptError = null;
    this.forumService.acceptAnswer(this.slug, commentId).subscribe({
      next: () => {
        if (this.question) {
          this.question.accepted_comment = commentId;
        }
      },
      error: () => {
        this.acceptError = 'Ошибка при отметке решения';
      }
    });
  }
}
