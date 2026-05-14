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
      question: 'What is this place?',
      answer: 'A personal platform where I build and host my projects — some are public, some are private. Think of it as my corner of the internet.',
    },
    {
      question: 'How do I sign in?',
      answer: 'Just hit "Sign in" and use your Google account. That\'s it — no registration, no forms.',
    },
  ];

  toggle(index: number): void {
    this.openIndex.set(this.openIndex() === index ? null : index);
  }
}
