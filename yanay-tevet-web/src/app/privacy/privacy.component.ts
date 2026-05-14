import { Component } from '@angular/core';
import { SUPPORT_EMAIL } from '../common/constants/app-constants';

@Component({
  selector: 'app-privacy',
  standalone: true,
  imports: [],
  templateUrl: './privacy.component.html',
})
export class PrivacyComponent {
  readonly lastUpdated = 'May 2026';
  readonly email = SUPPORT_EMAIL;
}
