import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BlockType, ContentBlock, CourseDetail, CourseService, Section } from 'src/app/core/services/course.service';
import { ForumService, Question } from 'src/app/core/services/forum.service';
import { AuthService, User } from 'src/app/core/services/auth.service';

interface FlatLesson {
  section: Section;
  block: ContentBlock;
}

@Component({
  selector: 'app-course-player',
  templateUrl: './course-player.component.html',
  styleUrls: ['./course-player.component.scss']
})
export class CoursePlayerComponent implements OnInit {
  courseId!: number;
  course: CourseDetail | null = null;
  isLoading = true;
  currentUser: User | null = null;
  isFavorited = false;

  selectedBlockId: number | null = null;
  isTogglingComplete = false;

  relatedQuestions: Question[] = [];
  isLoadingQuestions = false;

  sidebarOpen = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private courseService: CourseService,
    private forumService: ForumService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.router.navigate(['/courses']);
      return;
    }
    this.courseId = +id;

    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    this.loadCourse();
  }

  loadCourse(): void {
    this.courseService.getCourse(this.courseId).subscribe({
      next: (course) => {
        this.course = course;
        this.isLoading = false;

        const flat = this.flatLessons;
        const requestedId = Number(this.route.snapshot.queryParamMap.get('lesson'));
        const target =
          flat.find(f => f.block.id === requestedId)?.block ||
          flat.find(f => !f.block.is_completed)?.block ||
          flat[0]?.block;

        if (target) {
          this.selectLesson(target, true);
        }
      },
      error: () => {
        this.isLoading = false;
        this.router.navigate(['/courses']);
      }
    });
  }

  get flatLessons(): FlatLesson[] {
    if (!this.course) return [];
    const flat: FlatLesson[] = [];
    for (const section of this.course.sections) {
      for (const block of section.blocks) {
        flat.push({ section, block });
      }
    }
    return flat;
  }

  get selectedEntry(): FlatLesson | null {
    return this.flatLessons.find(f => f.block.id === this.selectedBlockId) || null;
  }

  get selectedIndex(): number {
    return this.flatLessons.findIndex(f => f.block.id === this.selectedBlockId);
  }

  get completedCount(): number {
    return this.flatLessons.filter(f => f.block.is_completed).length;
  }

  get progressPercent(): number {
    const total = this.flatLessons.length;
    return total === 0 ? 0 : Math.round((this.completedCount / total) * 100);
  }

  get hasPrev(): boolean {
    return this.selectedIndex > 0;
  }

  get hasNext(): boolean {
    const idx = this.selectedIndex;
    return idx >= 0 && idx < this.flatLessons.length - 1;
  }

  selectLesson(block: ContentBlock, isInitial = false): void {
    this.selectedBlockId = block.id;
    this.sidebarOpen = false;
    this.loadRelatedQuestions();

    if (!isInitial) {
      this.router.navigate([], {
        relativeTo: this.route,
        queryParams: { lesson: block.id },
        replaceUrl: true
      });
    }
  }

  goPrev(): void {
    if (this.hasPrev) {
      this.selectLesson(this.flatLessons[this.selectedIndex - 1].block);
    }
  }

  goNext(): void {
    if (this.hasNext) {
      this.selectLesson(this.flatLessons[this.selectedIndex + 1].block);
    }
  }

  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  toggleComplete(): void {
    const block = this.selectedEntry?.block;
    if (!block || this.isTogglingComplete) return;

    this.isTogglingComplete = true;
    this.courseService.toggleLessonComplete(block.id).subscribe({
      next: (res) => {
        block.is_completed = res.completed;
        this.isTogglingComplete = false;
      },
      error: () => this.isTogglingComplete = false
    });
  }

  toggleFavorite(): void {
    if (!this.course) return;
    this.courseService.toggleFavorite(this.course.id).subscribe({
      next: (res) => this.isFavorited = res.favorited
    });
  }

  loadRelatedQuestions(): void {
    if (!this.course?.category) {
      this.relatedQuestions = [];
      return;
    }
    this.isLoadingQuestions = true;
    this.forumService.getQuestions({ category: this.course.category.id }).subscribe({
      next: (res) => {
        const all = (res as any).results || res;
        this.relatedQuestions = all.slice(0, 4);
        this.isLoadingQuestions = false;
      },
      error: () => this.isLoadingQuestions = false
    });
  }

  askQuestion(): void {
    if (!this.course) return;
    const entry = this.selectedEntry;

    const contextLines = [`Курс: ${this.course.title}`];
    if (entry) {
      contextLines.push(`Урок: ${entry.block.title || this.blockTypeLabel(entry.block.type)}`);
    }

    this.router.navigate(['/forum/ask'], {
      queryParams: {
        category: this.course.category?.id || '',
        context: contextLines.join('\n') + '\n\n'
      }
    });
  }

  blockTypeLabel(type: BlockType): string {
    switch (type) {
      case 'text': return 'Текст';
      case 'video_link': return 'Видео';
      case 'link': return 'Ссылка';
      case 'media': return 'Файл';
      default: return type;
    }
  }
}
