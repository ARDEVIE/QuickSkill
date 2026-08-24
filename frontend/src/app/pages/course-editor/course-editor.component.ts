import { Component, HostListener, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { BlockType, Category, ContentBlock, CourseDetail, CourseService, Section } from 'src/app/core/services/course.service';
import { AuthService, User } from 'src/app/core/services/auth.service';

type SaveState = 'idle' | 'saving' | 'saved' | 'error';

@Component({
  selector: 'app-course-editor',
  templateUrl: './course-editor.component.html',
  styleUrls: ['./course-editor.component.scss']
})
export class CourseEditorComponent implements OnInit {
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

  /** Key of the currently open contextual (kebab) menu, e.g. "section-3" or "block-12". */
  openMenuFor: string | null = null;

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

  @HostListener('document:click')
  closeContextualMenu(): void {
    this.openMenuFor = null;
  }

  toggleMenu(key: string, event: Event): void {
    event.stopPropagation();
    this.openMenuFor = this.openMenuFor === key ? null : key;
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
    this.openMenuFor = null;
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

  moveSection(section: Section, direction: -1 | 1): void {
    if (!this.course) return;
    const sections = this.course.sections;
    const index = sections.indexOf(section);
    const swapIndex = index + direction;
    if (swapIndex < 0 || swapIndex >= sections.length) return;

    const neighbor = sections[swapIndex];
    [sections[index], sections[swapIndex]] = [sections[swapIndex], sections[index]];

    this.courseService.updateSection(section.id, { order: swapIndex }).subscribe();
    this.courseService.updateSection(neighbor.id, { order: index }).subscribe();
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

  selectBlock(section: Section, block: ContentBlock): void {
    this.selectedSectionId = section.id;
    this.selectedBlockId = block.id;
  }

  /** One click, no typing required: creates an empty lesson and selects it. Its content type is chosen afterwards via "+ Добавить содержимое". */
  addLesson(): void {
    if (!this.course || this.course.sections.length === 0) return;
    const section = this.selectedSection || this.course.sections[0];

    const formData = new FormData();
    formData.append('type', 'text');
    formData.append('title', 'Новый урок');
    formData.append('content', '');
    formData.append('order', String(section.blocks.length));

    this.courseService.addBlock(section.id, formData).subscribe({
      next: (block) => {
        section.blocks.push(block);
        this.selectBlock(section, block);
      }
    });
  }

  moveBlock(section: Section, block: ContentBlock, direction: -1 | 1): void {
    const index = section.blocks.indexOf(block);
    const swapIndex = index + direction;
    if (swapIndex < 0 || swapIndex >= section.blocks.length) return;

    const neighbor = section.blocks[swapIndex];
    [section.blocks[index], section.blocks[swapIndex]] = [section.blocks[swapIndex], section.blocks[index]];

    this.courseService.updateBlock(block.id, { order: swapIndex } as any).subscribe();
    this.courseService.updateBlock(neighbor.id, { order: index } as any).subscribe();
  }

  /** Blocks the author has explicitly given a content type to — dismisses the chooser even when the
   * chosen type matches the model default ('text'), which wouldn't otherwise trigger any change. */
  private activatedBlockIds = new Set<number>();

  /** Empty lesson (just created, nothing typed/attached yet) — content type hasn't been chosen. */
  isEmptyBlock(block: ContentBlock): boolean {
    if (this.activatedBlockIds.has(block.id)) return false;
    return block.type === 'text' && !block.content && !block.file;
  }

  /** "+ Добавить содержимое" — sets the lesson's content type. No modal: reveals the matching inline editor. */
  setBlockType(block: ContentBlock, type: BlockType, fileInput?: HTMLInputElement): void {
    if (type === 'media') {
      fileInput?.click();
      return;
    }
    this.activatedBlockIds.add(block.id);
    if (block.type === type) return;

    block.type = type;
    this.saveState = 'saving';
    this.courseService.updateBlock(block.id, { type } as any).subscribe({
      next: () => this.saveState = 'saved',
      error: () => this.saveState = 'error'
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

  onBlockFileSelect(event: any, block: ContentBlock): void {
    const file = event.target.files[0];
    if (!file) return;
    this.activatedBlockIds.add(block.id);
    const formData = new FormData();
    formData.append('type', 'media');
    formData.append('file', file);
    this.saveState = 'saving';
    this.courseService.updateBlock(block.id, formData).subscribe({
      next: (res) => {
        block.type = 'media';
        block.file = res.file;
        this.saveState = 'saved';
      },
      error: () => this.saveState = 'error'
    });
  }

  deleteBlock(section: Section, block: ContentBlock): void {
    this.openMenuFor = null;
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
