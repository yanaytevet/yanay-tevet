import {Component} from '@angular/core';
import {SUPPORT_EMAIL} from '../common/constants/app-constants';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [],
  templateUrl: './contact.component.html',
})
export class ContactComponent {
  readonly supportEmail = SUPPORT_EMAIL;
}
