import {Component} from '@angular/core';
import {SUPPORT_EMAIL} from '../common/constants/app-constants';
import {injectStrings} from '../shared/i18n/strings';
import {CONTACT_STRINGS} from './i18n';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [],
  templateUrl: './contact.component.html',
})
export class ContactComponent {
  protected readonly t = injectStrings(CONTACT_STRINGS);
  readonly supportEmail = SUPPORT_EMAIL;
}
