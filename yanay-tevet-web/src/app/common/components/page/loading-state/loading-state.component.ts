import {Component, input} from '@angular/core';

// The line a page shows while its resource loads. Never a card, so the layout doesn't jump when the
// content arrives.
@Component({
  selector: 'app-loading-state',
  templateUrl: './loading-state.component.html',
})
export class LoadingStateComponent {
  readonly label = input<string>('Loading');
}
