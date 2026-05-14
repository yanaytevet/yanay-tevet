import {Component, input, output} from '@angular/core';


@Component({
  selector: 'app-confirmation-button',
  templateUrl: './confirmation-button.component.html',
  standalone: true,
  imports: []
})
export class ConfirmationButtonComponent {
  disabled = input<boolean>(false);
  text = input<string>('Submit');
  clicked = output<void>();

  onClick(): void {
    if (!this.disabled()) {
      this.clicked.emit();
    }
  }
}
