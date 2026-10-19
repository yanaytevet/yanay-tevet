import {Component, input} from '@angular/core';
import {RouterLink, RouterLinkActive, UrlTree} from '@angular/router';

export interface SubNavLink {
  label: string;
  url: UrlTree;
  // Active only on this exact URL, not on the pages under it.
  exact?: boolean;
}

// An app's section links, as a bar under the top header. Its width matches the page container under it.
@Component({
  selector: 'app-sub-nav',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './sub-nav.component.html',
})
export class SubNavComponent {
  readonly links = input.required<SubNavLink[]>();
  readonly width = input<'narrow' | 'wide'>('wide');
}
