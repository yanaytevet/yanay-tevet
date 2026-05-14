import {Component, signal} from '@angular/core';
import {SUPPORT_EMAIL} from '../common/constants/app-constants';

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
  readonly openIndex = signal<number | null>(null);
  readonly supportEmail = SUPPORT_EMAIL;

  readonly items: FaqItem[] = [
    {
      question: 'What is Yanay Tevet?',
      answer: 'Yanay Tevet is a web application. Sign in to get started.',
    },
    {
      question: 'Is Yanay Tevet free to use?',
      answer: 'Yes — Yanay Tevet is currently in open beta and free to use.',
    },
    {
      question: 'How do I get support?',
      answer: `If you have questions or run into any issues, reach out to us at ${SUPPORT_EMAIL}.`,
    },
  ];

  toggle(index: number): void {
    this.openIndex.set(this.openIndex() === index ? null : index);
  }
}
