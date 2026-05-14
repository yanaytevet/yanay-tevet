import {UrlTree} from '@angular/router';

export interface BreadcrumbSegment {
  label: string;
  link?: string | string[] | UrlTree;
}

export interface BreadcrumbContextChip {
  label: string;
  link: string | string[] | UrlTree;
}

export interface LayoutBreadcrumbData {
  depth: number;
  segments: BreadcrumbSegment[];
  contextChip?: BreadcrumbContextChip;
}
