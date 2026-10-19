import {Component, input} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherCheck} from '@ng-icons/feather-icons';

// The one checkbox look (DESIGN.md §5, Checkboxes): a box that fills with the accent when checked. Only the
// visual — the caller wraps it in its own button (aria-pressed, ≥32px hit area, `group/check` for the hover).
@Component({
  selector: 'app-checkbox-mark',
  imports: [NgIcon],
  templateUrl: './checkbox-mark.component.html',
  host: {class: 'contents'},
})
export class CheckboxMarkComponent {
  readonly checked = input.required<boolean>();
  readonly size = input<'sm' | 'md'>('md');

  protected readonly featherCheck = featherCheck;
}
