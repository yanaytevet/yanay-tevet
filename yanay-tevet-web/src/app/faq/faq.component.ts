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
      answer: 'Yanay Tevet is a private platform. Access is by invitation only.',
    },
    {
      question: 'How do I get access?',
      answer: `Reach out directly at ${SUPPORT_EMAIL} to request access.`,
    },
    {
      question: 'I already have an account — how do I get support?',
      answer: `Sign in and contact us at ${SUPPORT_EMAIL}. We'll get back to you as soon as possible.`,
    },
  ];

  toggle(index: number): void {
    this.openIndex.set(this.openIndex() === index ? null : index);
  }
}
