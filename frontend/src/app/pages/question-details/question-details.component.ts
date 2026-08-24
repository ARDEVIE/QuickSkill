import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
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
  isFavorited = false;
  currentUser: User | null = null;

  commentForm: FormGroup;
  isSubmitting = false;
  selectedFile: File | null = null;

  constructor(
    private route: ActivatedRoute,
    private forumService: ForumService,
    private authService: AuthService,
    private fb: FormBuilder,
    private router: Router
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
      this.isFavorited = !!res.is_favorited;
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

  toggleFavorite(): void {
    if (!this.slug) return;
    this.forumService.toggleFavorite(this.slug).subscribe({
      next: (res) => {
        this.isFavorited = res.favorited;
      }
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
    }
  }

  onAddComment(): void {
    if (this.commentForm.invalid) return;

    this.isSubmitting = true;
    
    const formData = new FormData();
    formData.append('content', this.commentForm.get('content')?.value);
    
    if (this.selectedFile) {
      formData.append('media_file', this.selectedFile);
    }

    this.forumService.addComment(this.slug, formData).subscribe({
      next: (comment) => {
        this.comments.push(comment);
        if (this.question) this.question.answer_count++;
        this.commentForm.reset();
        this.selectedFile = null;
        this.isSubmitting = false;
      },
      error: () => {
        this.isSubmitting = false;
        alert('Ошибка при отправке ответа');
      }
    });
  }

  questionTags(): string[] {
    if (!this.question) return [];
    return (this.question.tags || '').split(',').map(t => t.trim()).filter(Boolean);
  }

  voteQuestion(value: 1 | -1): void {
    if (!this.isLoggedIn || !this.question) return;
    this.forumService.voteQuestion(this.slug, value).subscribe(res => {
      if (!this.question) return;
      this.question.vote_score = res.vote_score;
      this.question.user_vote = res.user_vote;
    });
  }

  voteComment(comment: Comment, value: 1 | -1): void {
    if (!this.isLoggedIn) return;
    this.forumService.voteComment(comment.id, value).subscribe(res => {
      comment.vote_score = res.vote_score;
      comment.user_vote = res.user_vote;
    });
  }

  acceptAnswer(commentId: number): void {
    if (!this.question) return;
    this.forumService.acceptAnswer(this.slug, commentId).subscribe({
      next: () => {
        if (this.question) this.question.accepted_comment = commentId;
      },
      error: () => alert('Ошибка при принятии решения')
    });
  }

  deleteQuestion(): void {
    if (confirm('Вы уверены, что хотите удалить этот вопрос?')) {
      this.forumService.deleteQuestion(this.slug).subscribe({
        next: () => {
          this.router.navigate(['/forum']);
        },
        error: () => alert('Ошибка при удалении вопроса')
      });
    }
  }
}
