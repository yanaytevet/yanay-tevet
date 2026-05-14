import { Component } from '@angular/core';
import { SUPPORT_EMAIL } from '../common/constants/app-constants';

@Component({
  selector: 'app-terms',
  standalone: true,
  imports: [],
  templateUrl: './terms.component.html',
})
export class TermsComponent {
  readonly lastUpdated = 'May 2026';
  readonly email = SUPPORT_EMAIL;
}
