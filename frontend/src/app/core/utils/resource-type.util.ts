import { ResourceType } from '../services/subject.service';

const YOUTUBE_RE = /(youtube\.com|youtu\.be|vimeo\.com)/i;
const IMAGE_EXT_RE = /\.(png|jpe?g|gif|webp|svg)$/i;
const PDF_EXT_RE = /\.pdf$/i;

export const RESOURCE_TYPE_LABELS: Record<ResourceType, string> = {
  pdf: 'PDF',
  document: 'Документ',
  image: 'Изображение',
  notes: 'Конспект',
  cheatsheet: 'Шпаргалка',
  past_paper: 'Прошлый экзамен',
  link: 'Ссылка',
  video: 'Видео',
};

export function resourceTypeLabel(type: ResourceType): string {
  return RESOURCE_TYPE_LABELS[type] || type;
}

export interface ResourceTag {
  value: string;
  label: string;
}

export const RESOURCE_TAGS: ResourceTag[] = [
  { value: 'midterm', label: 'Midterm' },
  { value: 'final', label: 'Final' },
  { value: 'lecture_notes', label: 'Lecture Notes' },
  { value: 'past_paper', label: 'Past Paper' },
  { value: 'cheat_sheet', label: 'Cheat Sheet' },
  { value: 'assignment', label: 'Assignment' },
];

export function resourceTagLabel(value: string): string {
  return RESOURCE_TAGS.find(t => t.value === value)?.label || value;
}

/** Infers a content type from a dropped/selected file — no manual type picker needed. */
export function detectTypeFromFile(file: File): ResourceType {
  if (PDF_EXT_RE.test(file.name)) return 'pdf';
  if (IMAGE_EXT_RE.test(file.name)) return 'image';
  return 'document';
}

/** Infers a content type from a pasted URL — no manual type picker needed. */
export function detectTypeFromUrl(url: string): ResourceType {
  return YOUTUBE_RE.test(url) ? 'video' : 'link';
}

/** Best-effort human title from a filename: strips the extension, swaps separators for spaces, capitalizes. */
export function titleFromFilename(filename: string): string {
  const base = filename.replace(/\.[^./\\]+$/, '').replace(/[-_]+/g, ' ').trim();
  return base.charAt(0).toUpperCase() + base.slice(1);
}

/** Best-effort human title from a URL: last meaningful path segment, or the hostname. */
export function titleFromUrl(url: string): string {
  try {
    const parsed = new URL(url);
    const segments = parsed.pathname.split('/').filter(Boolean);
    const last = segments[segments.length - 1];
    if (last) {
      return titleFromFilename(decodeURIComponent(last));
    }
    return parsed.hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}
