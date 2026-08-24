import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { BlockType, Category, ContentBlock, CourseDetail, CourseService, Section } from 'src/app/core/services/course.service';
import { AuthService, User } from 'src/app/core/services/auth.service';

type SaveState = 'idle' | 'saving' | 'saved' | 'error';

const YOUTUBE_RE = /(youtube\.com|youtu\.be|vimeo\.com)/i;
const URL_RE = /^https?:\/\/\S+$/i;

@Component({
  selector: 'app-course-editor',
  templateUrl: './course-editor.component.html',
  styleUrls: ['./course-editor.component.scss']
})
export class CourseEditorComponent implements OnInit {
  @ViewChild('quickAddInput') quickAddInputRef?: ElementRef<HTMLTextAreaElement>;

  courseId!: number;
  course: CourseDetail | null = null;
  isLoading = true;
  currentUser: User | null = null;

  categories: Category[] = [];
  settingsOpen = false;
  settingsForm: FormGroup;
  settingsFile: File | null = null;
  isSavingSettings = false;

  selectedSectionId: number | null = null;
  selectedBlockId: number | null = null;

  addingSection = false;
  newSectionTitle = '';

  quickAddValue = '';
  quickAddFile: File | null = null;
  quickAddError: string | null = null;

  saveState: SaveState = 'idle';
  private saveTimers = new Map<string, any>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private fb: FormBuilder,
    private courseService: CourseService,
    private authService: AuthService
  ) {
    this.settingsForm = this.fb.group({
      category: ['', Validators.required],
      description: ['']
    });
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.router.navigate(['/courses']);
      return;
    }
    this.courseId = +id;

    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      this.checkAuthor();
    });

    this.courseService.getCategories().subscribe(res => {
      this.categories = (res as any).results || res;
    });

    this.loadCourse();
  }

  loadCourse(): void {
    this.courseService.getCourse(this.courseId).subscribe({
      next: (course) => {
        this.course = course;
        this.isLoading = false;
        this.settingsForm.patchValue({
          category: course.category?.id || '',
          description: course.description
        });
        this.checkAuthor();

        if (!this.selectedBlockId && course.sections.length > 0) {
          const firstWithBlocks = course.sections.find(s => s.blocks.length > 0);
          if (firstWithBlocks) {
            this.selectBlock(firstWithBlocks, firstWithBlocks.blocks[0]);
          } else {
            this.selectedSectionId = course.sections[0].id;
          }
        }
      },
      error: () => {
        this.isLoading = false;
        this.router.navigate(['/courses']);
      }
    });
  }

  checkAuthor(): void {
    if (this.course && this.currentUser && this.course.author.id !== this.currentUser.id) {
      this.router.navigate(['/courses', this.courseId]);
    }
  }

  // ---------- Title (top bar, inline) ----------

  onTitleInput(value: string): void {
    if (!this.course) return;
    this.course.title = value;
    this.debounce('title', () => this.saveCourseField({ title: value }));
  }

  // ---------- Settings (progressive disclosure: category / description / cover) ----------

  toggleSettings(): void {
    this.settingsOpen = !this.settingsOpen;
  }

  onSettingsFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) this.settingsFile = file;
  }

  saveSettings(): void {
    if (!this.course || this.settingsForm.invalid) return;
    this.isSavingSettings = true;

    const formData = new FormData();
    formData.append('category', this.settingsForm.get('category')?.value);
    formData.append('description', this.settingsForm.get('description')?.value || '');
    if (this.settingsFile) {
      formData.append('cover', this.settingsFile);
    }

    this.courseService.updateCourse(this.courseId, formData).subscribe({
      next: (res) => {
        if (this.course) {
          this.course.category = res.category;
          this.course.description = res.description;
          this.course.cover = res.cover;
        }
        this.settingsFile = null;
        this.isSavingSettings = false;
        this.settingsOpen = false;
      },
      error: () => {
        this.isSavingSettings = false;
      }
    });
  }

  // ---------- Publish / Preview ----------

  togglePublish(): void {
    if (!this.course) return;
    const nextState = !this.course.is_published;
    this.courseService.updateCourse(this.courseId, { is_published: nextState } as any).subscribe({
      next: () => {
        if (this.course) this.course.is_published = nextState;
      }
    });
  }

  openPreview(): void {
    window.open(`/courses/${this.courseId}`, '_blank');
  }

  // ---------- Sections ----------

  toggleAddSection(): void {
    this.addingSection = !this.addingSection;
    this.newSectionTitle = '';
  }

  confirmAddSection(): void {
    if (!this.course || !this.newSectionTitle.trim()) return;
    const title = this.newSectionTitle.trim();

    this.courseService.addSection(this.courseId, { title, order: this.course.sections.length }).subscribe({
      next: (section) => {
        section.blocks = section.blocks || [];
        this.course?.sections.push(section);
        this.selectedSectionId = section.id;
        this.addingSection = false;
        this.newSectionTitle = '';
      }
    });
  }

  onSectionTitleInput(section: Section, value: string): void {
    section.title = value;
    this.debounce(`section-${section.id}`, () => {
      this.saveState = 'saving';
      this.courseService.updateSection(section.id, { title: value }).subscribe({
        next: () => this.saveState = 'saved',
        error: () => this.saveState = 'error'
      });
    });
  }

  deleteSection(section: Section): void {
    if (!confirm(`Удалить раздел «${section.title}» вместе со всеми уроками?`)) return;
    this.courseService.deleteSection(section.id).subscribe({
      next: () => {
        if (!this.course) return;
        this.course.sections = this.course.sections.filter(s => s.id !== section.id);
        if (this.selectedSectionId === section.id) {
          this.selectedSectionId = null;
          this.selectedBlockId = null;
        }
      }
    });
  }

  // ---------- Lessons (blocks) ----------

  get selectedSection(): Section | null {
    return this.course?.sections.find(s => s.id === this.selectedSectionId) || null;
  }

  get selectedBlock(): ContentBlock | null {
    return this.selectedSection?.blocks.find(b => b.id === this.selectedBlockId) || null;
  }

  selectSection(section: Section): void {
    this.selectedSectionId = section.id;
    this.selectedBlockId = null;
  }

  /** "+ Добавить урок" in the curriculum column — targets the active (or first) section and hands off to the always-visible quick-add row on the right, instead of opening a separate creation flow. */
  focusAddLesson(): void {
    if (!this.selectedSectionId && this.course?.sections.length) {
      this.selectedSectionId = this.course.sections[this.course.sections.length - 1].id;
    }
    setTimeout(() => this.quickAddInputRef?.nativeElement.focus());
  }

  selectBlock(section: Section, block: ContentBlock): void {
    this.selectedSectionId = section.id;
    this.selectedBlockId = block.id;
    this.quickAddValue = '';
    this.quickAddFile = null;
    this.quickAddError = null;
  }

  onQuickAddFileSelect(event: any): void {
    const file = event.target.files[0];
    if (file) this.quickAddFile = file;
  }

  /** Detects text/video/link/media from what the author just typed or attached — no type picker. */
  private detectBlockType(): BlockType {
    if (this.quickAddFile) return 'media';
    const value = this.quickAddValue.trim();
    if (YOUTUBE_RE.test(value)) return 'video_link';
    if (URL_RE.test(value)) return 'link';
    return 'text';
  }

  submitQuickAdd(): void {
    const targetSectionId = this.selectedSectionId || this.course?.sections[0]?.id;
    if (!targetSectionId) {
      this.quickAddError = 'Сначала добавь раздел.';
      return;
    }
    if (!this.quickAddValue.trim() && !this.quickAddFile) return;

    const section = this.course?.sections.find(s => s.id === targetSectionId);
    if (!section) return;

    const type = this.detectBlockType();
    const formData = new FormData();
    formData.append('type', type);
    formData.append('order', String(section.blocks.length));

    if (type === 'media' && this.quickAddFile) {
      formData.append('file', this.quickAddFile);
      formData.append('title', this.quickAddFile.name);
    } else {
      formData.append('content', this.quickAddValue.trim());
      if (type === 'text') {
        formData.append('title', this.quickAddValue.trim().slice(0, 60));
      }
    }

    this.quickAddError = null;

    this.courseService.addBlock(targetSectionId, formData).subscribe({
      next: (block) => {
        section.blocks.push(block);
        this.selectBlock(section, block);
      },
      error: () => {
        this.quickAddError = 'Не удалось добавить урок.';
      }
    });
  }

  onBlockTitleInput(block: ContentBlock, value: string): void {
    block.title = value;
    this.debounce(`block-title-${block.id}`, () => this.saveBlockField(block, { title: value }));
  }

  onBlockContentInput(block: ContentBlock, value: string): void {
    block.content = value;
    this.debounce(`block-content-${block.id}`, () => this.saveBlockField(block, { content: value }));
  }

  onBlockFileReplace(event: any, block: ContentBlock): void {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    this.saveState = 'saving';
    this.courseService.updateBlock(block.id, formData).subscribe({
      next: (res) => {
        block.file = res.file;
        this.saveState = 'saved';
      },
      error: () => this.saveState = 'error'
    });
  }

  deleteBlock(section: Section, block: ContentBlock): void {
    if (!confirm('Удалить этот урок?')) return;
    this.courseService.deleteBlock(block.id).subscribe({
      next: () => {
        section.blocks = section.blocks.filter(b => b.id !== block.id);
        if (this.selectedBlockId === block.id) {
          this.selectedBlockId = null;
        }
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

  totalLessons(): number {
    return this.course?.sections.reduce((sum, s) => sum + s.blocks.length, 0) || 0;
  }

  // ---------- helpers ----------

  private saveBlockField(block: ContentBlock, patch: Partial<Pick<ContentBlock, 'title' | 'content'>>): void {
    this.saveState = 'saving';
    this.courseService.updateBlock(block.id, patch).subscribe({
      next: () => this.saveState = 'saved',
      error: () => this.saveState = 'error'
    });
  }

  private saveCourseField(patch: any): void {
    this.saveState = 'saving';
    this.courseService.updateCourse(this.courseId, patch).subscribe({
      next: () => this.saveState = 'saved',
      error: () => this.saveState = 'error'
    });
  }

  private debounce(key: string, fn: () => void, delay = 700): void {
    clearTimeout(this.saveTimers.get(key));
    this.saveTimers.set(key, setTimeout(fn, delay));
  }
}
