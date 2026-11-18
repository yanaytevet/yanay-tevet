import {Component, computed, signal} from '@angular/core';
import {SUPPORT_EMAIL} from '../common/constants/app-constants';
import {injectStrings} from '../shared/i18n/strings';
import {FAQ_STRINGS} from './i18n';

interface FaqItem {
  question: string;
  answer: string;
}

@Component({
  selector: 'app-faq',
  standalone: true,
  imports: [],
  templateUrl: './faq.component.html',
})
export class FaqComponent {
  protected readonly t = injectStrings(FAQ_STRINGS);
  readonly openIndex = signal<number | null>(null);
  readonly supportEmail = SUPPORT_EMAIL;

  readonly items = computed<FaqItem[]>(() => [this.t().whatIsThis, this.t().howToSignIn]);

  toggle(index: number): void {
    this.openIndex.set(this.openIndex() === index ? null : index);
  }
}
