import {Component, computed, inject, input} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {AppAccentService} from '../../../../shared/apps/app-accent.service';

// What a list shows when it has nothing in it: an invitation, not an apology. The call to action is
// projected.
@Component({
  selector: 'app-empty-state',
  imports: [NgIcon],
  templateUrl: './empty-state.component.html',
})
export class EmptyStateComponent {
  private readonly appAccentService = inject(AppAccentService);

  readonly title = input.required<string>();
  readonly text = input<string | null>(null);
  readonly icon = input<string | null>(null);

  protected readonly chipIcon = computed(() => this.icon() ?? this.appAccentService.currentApp()?.icon ?? null);
}
