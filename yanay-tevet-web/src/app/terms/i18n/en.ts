// Strings for the terms & conditions. This file is the contract: every other language's file is typed against it.
// Legal text: translations are full and faithful, and each one opens with `translationNotice` saying the English
// version is the binding one (empty here, so English shows no notice). The contact email sits between
// `beforeEmail` and `afterEmail`.
export const en = {
  translationNotice: '',
  lastUpdated: 'Last updated: {date}',
  title: 'Terms & Conditions',
  subtitle: 'Please read these terms carefully before using Yanay Tevet.',
  acceptance: {
    title: '1. Acceptance of Terms',
    body: 'By accessing or using Yanay Tevet, you agree to be bound by these Terms & Conditions. If you do not agree with any part of these terms, you may not access the service.',
  },
  eligibility: {
    title: '2. Eligibility',
    body: 'You must be at least 13 years old to use Yanay Tevet. By using the service, you confirm that you meet this requirement. If you are under 18, you represent that you have parental or guardian consent.',
  },
  use: {
    title: '3. Use of the Service',
    body: 'Yanay Tevet is a web platform. You may use the service for personal or professional purposes as long as your use complies with these terms. You are responsible for all activity that occurs under your account.',
  },
  accounts: {
    title: '4. User Accounts',
    body: 'Access to Yanay Tevet requires a user account. You are responsible for keeping your credentials confidential. You must not share your account with others or create accounts on behalf of third parties without authorization.',
  },
  prohibited: {
    title: '5. Prohibited Activities',
    intro: 'You agree not to:',
    items: [
      'Use the service for any unlawful purpose or in violation of any regulations',
      'Attempt to gain unauthorized access to any part of the service',
      'Upload or transmit harmful, offensive, abusive, or infringing content',
      'Interfere with or disrupt the integrity or performance of the service',
      'Reverse-engineer or attempt to extract the source code of the platform',
    ] as [string, string, string, string, string],
  },
  content: {
    title: '6. Your Content',
    body: 'All content you create on Yanay Tevet remains your property. By uploading or creating content on the platform, you grant Yanay Tevet a limited, non-exclusive license to host, store, process, back up, and display that content as necessary to operate and provide the service, including for security, abuse prevention, legal compliance, and system maintenance. We do not claim ownership over your content and will not use it for marketing or commercial purposes without your consent.',
  },
  moderation: {
    title: '7. Content Moderation',
    body: 'We reserve the right to remove or restrict content, and to suspend or terminate accounts, that we determine in our reasonable judgment to be abusive, harmful, illegal, or infringing on third-party rights. We may act without prior notice where necessary to protect users, maintain service integrity, or comply with legal obligations.',
  },
  ip: {
    title: '8. Intellectual Property',
    body: 'Yanay Tevet platform — its design, features, and code — is owned by Yanay Tevet and its developer, and protected by applicable intellectual property laws. Nothing in these terms transfers any platform IP to you.',
  },
  availability: {
    title: '9. Service Availability and Data Preservation',
    body: 'We aim to keep Yanay Tevet available and your data intact, but we do not guarantee uninterrupted access or permanent data preservation. The service may experience downtime, data loss, or be discontinued. You are responsible for keeping backups of any content you consider important.',
  },
  termination: {
    title: '10. Termination',
    body: 'We reserve the right to suspend or terminate your access to the service at any time, with or without notice, for conduct that we determine violates these terms or is otherwise harmful to other users, the platform, or third parties.',
  },
  warranties: {
    title: '11. Disclaimer of Warranties',
    body: 'The service is provided on an “as is” and “as available” basis without warranties of any kind, either express or implied. We do not warrant that the service will be uninterrupted, error-free, or free from harmful components.',
  },
  liability: {
    title: '12. Limitation of Liability',
    body: 'To the fullest extent permitted by law, Yanay Tevet and its operators shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to loss of data, loss of profits, or business interruption, arising out of or in connection with your use of the service, even if we have been advised of the possibility of such damages.',
  },
  changes: {
    title: '13. Changes to Terms',
    body: 'We may update these terms from time to time. We will notify users of significant changes by updating the date at the top of this page. Continued use of the service after changes constitutes acceptance of the revised terms.',
  },
  law: {
    title: '14. Governing Law',
    body: 'These Terms are governed by the laws of the State of Israel. Any disputes arising from these Terms or your use of the service shall be subject to the exclusive jurisdiction of the competent courts in Tel Aviv, Israel.',
  },
  contact: {
    title: '15. Contact',
    beforeEmail: 'Questions about these terms? Contact us at ',
    afterEmail: '.',
  },
};

export type TermsStrings = typeof en;
