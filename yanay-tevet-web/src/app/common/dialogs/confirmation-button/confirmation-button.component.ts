import {Component, computed, input, output} from '@angular/core';
import {COMMON_STRINGS} from '../../../common/i18n';
import {injectStrings} from '../../../shared/i18n/strings';


@Component({
  selector: 'app-confirmation-button',
  templateUrl: './confirmation-button.component.html',
  standalone: true,
  imports: []
})
export class ConfirmationButtonComponent {
  disabled = input<boolean>(false);
  // Without a text, the site language's "Submit".
  text = input<string | undefined>(undefined);
  protected readonly t = injectStrings(COMMON_STRINGS);
  protected readonly label = computed(() => this.text() ?? this.t().submit);
  clicked = output<void>();

  onClick(): void {
    if (!this.disabled()) {
      this.clicked.emit();
    }
  }
}
