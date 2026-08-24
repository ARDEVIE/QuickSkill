import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Course, CourseService } from 'src/app/core/services/course.service';
import { ForumService, Question } from 'src/app/core/services/forum.service';
import { AuthService, User } from 'src/app/core/services/auth.service';
import { Resource, ResourceType, SubjectDetail, SubjectService } from 'src/app/core/services/subject.service';
import { resourceTypeLabel } from 'src/app/core/utils/resource-type.util';

type Tab = 'overview' | 'materials' | 'guides' | 'questions';

@Component({
  selector: 'app-subject-detail',
  templateUrl: './subject-detail.component.html',
  styleUrls: ['./subject-detail.component.scss']
})
export class SubjectDetailComponent implements OnInit {
  subjectId!: number;
  subject: SubjectDetail | null = null;
  isLoading = true;
  currentUser: User | null = null;
  isTogglingFollow = false;

  activeTab: Tab = 'overview';

  // Overview
  overviewResources: Resource[] = [];
  overviewUnresolved: Question[] = [];
  overviewGuides: Course[] = [];
  isLoadingOverview = false;
  private overviewLoadedOnce = false;

  // Materials
  materials: Resource[] = [];
  materialsLoadedOnce = false;
  isLoadingMaterials = false;

  // Guides
  guides: Course[] = [];
  guidesLoadedOnce = false;
  isLoadingGuides = false;

  // Questions
  questions: Question[] = [];
  questionsLoadedOnce = false;
  isLoadingQuestions = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private subjectService: SubjectService,
    private courseService: CourseService,
    private forumService: ForumService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.router.navigate(['/subjects']);
      return;
    }
    this.subjectId = +id;

    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    this.loadSubject();
  }

  loadSubject(): void {
    this.subjectService.getSubject(this.subjectId).subscribe({
      next: (subject) => {
        this.subject = subject;
        this.isLoading = false;
        const requestedTab = this.route.snapshot.queryParamMap.get('tab') as Tab | null;
        const validTabs: Tab[] = ['overview', 'materials', 'guides', 'questions'];
        this.setTab(requestedTab && validTabs.includes(requestedTab) ? requestedTab : 'overview');
      },
      error: () => {
        this.isLoading = false;
        this.router.navigate(['/subjects']);
      }
    });
  }

  setTab(tab: Tab): void {
    this.activeTab = tab;
    if (tab === 'overview' && !this.overviewLoadedOnce) this.loadOverview();
    if (tab === 'materials' && !this.materialsLoadedOnce) this.loadMaterials();
    if (tab === 'guides' && !this.guidesLoadedOnce) this.loadGuides();
    if (tab === 'questions' && !this.questionsLoadedOnce) this.loadQuestions();
  }

  private loadOverview(): void {
    this.overviewLoadedOnce = true;
    this.isLoadingOverview = true;
    let pending = 3;
    const done = () => { if (--pending === 0) this.isLoadingOverview = false; };

    this.subjectService.getResources({ category: this.subjectId }).subscribe({
      next: (res) => { this.overviewResources = ((res as any).results || res).slice(0, 4); done(); },
      error: done
    });

    this.forumService.getQuestions({ category: this.subjectId, unresolved: 'true' }).subscribe({
      next: (res) => { this.overviewUnresolved = ((res as any).results || res).slice(0, 4); done(); },
      error: done
    });

    this.courseService.getCourses({ category: this.subjectId, public_only: 'true' }).subscribe({
      next: (res) => { this.overviewGuides = (res.results || []).slice(0, 4); done(); },
      error: done
    });
  }

  private loadMaterials(): void {
    this.materialsLoadedOnce = true;
    this.isLoadingMaterials = true;
    this.subjectService.getResources({ category: this.subjectId }).subscribe({
      next: (res) => {
        this.materials = (res as any).results || res;
        this.isLoadingMaterials = false;
      },
      error: () => this.isLoadingMaterials = false
    });
  }

  private loadGuides(): void {
    this.guidesLoadedOnce = true;
    this.isLoadingGuides = true;
    this.courseService.getCourses({ category: this.subjectId, public_only: 'true' }).subscribe({
      next: (res) => {
        this.guides = res.results || [];
        this.isLoadingGuides = false;
      },
      error: () => this.isLoadingGuides = false
    });
  }

  private loadQuestions(): void {
    this.questionsLoadedOnce = true;
    this.isLoadingQuestions = true;
    this.forumService.getQuestions({ category: this.subjectId }).subscribe({
      next: (res) => {
        this.questions = (res as any).results || res;
        this.isLoadingQuestions = false;
      },
      error: () => this.isLoadingQuestions = false
    });
  }

  toggleFollow(): void {
    if (!this.subject || this.isTogglingFollow) return;
    this.isTogglingFollow = true;
    this.subjectService.toggleFollow(this.subject.id).subscribe({
      next: (res) => {
        if (!this.subject) return;
        this.subject.is_following = res.following;
        this.subject.students_count += res.following ? 1 : -1;
        this.isTogglingFollow = false;
      },
      error: () => this.isTogglingFollow = false
    });
  }

  askQuestion(): void {
    if (!this.subject) return;
    this.router.navigate(['/forum/ask'], { queryParams: { category: this.subject.id } });
  }

  // ---------- Materials ----------

  shareMaterial(): void {
    this.router.navigate(['/share-material'], { queryParams: { subject: this.subjectId } });
  }

  deleteMaterial(resource: Resource): void {
    if (!confirm(`Удалить «${resource.title}»?`)) return;
    this.subjectService.deleteResource(resource.id).subscribe({
      next: () => {
        this.materials = this.materials.filter(m => m.id !== resource.id);
        if (this.subject) this.subject.materials_count--;
      }
    });
  }

  isOwnResource(resource: Resource): boolean {
    return !!this.currentUser && resource.author.id === this.currentUser.id;
  }

  resourceTypeLabel(type: ResourceType): string {
    return resourceTypeLabel(type);
  }
}
