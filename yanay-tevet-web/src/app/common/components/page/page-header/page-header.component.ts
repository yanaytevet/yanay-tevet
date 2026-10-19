import {Component, computed, inject, input} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {AppAccentService} from '../../../../shared/apps/app-accent.service';

// The top of every app page (DESIGN.md §5): the app chip, title, subtitle, and the page's actions
// projected on the right. Below `sm` the actions wrap under the title.
@Component({
  selector: 'app-page-header',
  imports: [NgIcon],
  templateUrl: './page-header.component.html',
})
export class PageHeaderComponent {
  private readonly appAccentService = inject(AppAccentService);

  readonly title = input.required<string>();
  readonly subtitle = input<string | null>(null);
  // Defaults to the current app's icon; a page outside any app passes its own or none.
  readonly icon = input<string | null>(null);

  protected readonly chipIcon = computed(() => this.icon() ?? this.appAccentService.currentApp()?.icon ?? null);
}
