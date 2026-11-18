// Strings for the FAQ page. This file is the contract: every other language's file is typed against it.
export const en = {
  title: 'Frequently asked questions',
  subtitle: 'What this place is and how to get in.',
  whatIsThis: {
    question: 'What is this place?',
    answer: 'A personal platform where I build and host my projects — some are public, some are private. Think of it as my corner of the internet.',
  },
  howToSignIn: {
    question: 'How do I sign in?',
    answer: 'Just hit “Sign in” and use your Google account. That’s it — no registration, no forms.',
  },
  somethingElse: 'Something else on your mind?',
  dropLineBefore: 'Drop me a line at ',
  dropLineAfter: '',
};

export type FaqStrings = typeof en;
