import {Component, effect, input, signal} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {bootstrapChevronDown, bootstrapChevronRight} from '@ng-icons/bootstrap-icons';

@Component({
  selector: 'app-collapsible-section',
  imports: [NgIcon],
  providers: [provideIcons({bootstrapChevronDown, bootstrapChevronRight})],
  templateUrl: './collapsible-section.component.html',
})
export class CollapsibleSectionComponent {
  readonly title = input.required<string>();
  readonly startOpen = input<boolean>(false);

  readonly isOpen = signal(false);

  constructor() {
    effect(() => {
      if (this.startOpen()) {
        this.isOpen.set(true);
      }
    });
  }

  toggle() {
    this.isOpen.set(!this.isOpen());
  }

  protected readonly bootstrapChevronDown = bootstrapChevronDown;
  protected readonly bootstrapChevronRight = bootstrapChevronRight;
}
