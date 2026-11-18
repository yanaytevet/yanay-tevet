// Strings for the privacy policy. This file is the contract: every other language's file is typed against it.
// Legal text: translations are full and faithful, and each one opens with `translationNotice` saying the English
// version is the binding one (empty here, so English shows no notice). A link or email inside a paragraph sits
// between a `before…` and an `after…` string.
export const en = {
  translationNotice: '',
  lastUpdated: 'Last updated: {date}',
  title: 'Privacy Policy',
  subtitle: 'How Yanay Tevet collects, uses, and protects your information.',
  collect: {
    title: '1. Information We Collect',
    intro: 'We collect information when you use the service, including:',
    items: [
      'Account information provided via Google Sign-In (name, email address, and profile picture as shared by Google)',
      'Content you create and manage on the platform',
      'Communications you send through the platform',
    ] as [string, string, string],
    technical: 'We may also collect technical information such as IP address, browser type, and usage data to operate and improve the service.',
  },
  use: {
    title: '2. How We Use Your Information',
    intro: 'We use the information we collect to:',
    items: [
      'Provide, maintain, and improve the service',
      'Authenticate your identity and secure your account',
      'Respond to your requests and support needs',
      'Monitor and analyze usage patterns to improve the platform',
    ] as [string, string, string, string],
  },
  security: {
    title: '3. Data Storage and Security',
    body: 'We apply industry-standard security measures to protect your information against unauthorized access, alteration, disclosure, or destruction. No method of transmission over the internet is 100% secure, and we cannot guarantee absolute security, but we take reasonable precautions to safeguard your data.',
  },
  retention: {
    title: '4. Data Retention',
    body: 'We retain your data for as long as your account is active or as needed to operate the service. If you delete your account, we will remove your personal data within a reasonable time, except where retention is required for legal compliance, security, fraud prevention, or backup integrity.',
  },
  thirdParty: {
    title: '5. Third-Party Services',
    beforeLink: 'We do not sell or rent your personal information. Authentication is handled via Google Sign-In — by using it you are also subject to ',
    link: 'Google’s Privacy Policy',
    afterLink: '. We may also share data with other third-party providers who help us operate the platform — such as hosting providers or error monitoring services. These providers access only the data necessary for their function and are bound by confidentiality obligations. We may also disclose information if required by law.',
  },
  cookies: {
    title: '6. Cookies',
    body: 'Yanay Tevet uses cookies solely to maintain your session and remember your preferences. We currently do not use advertising or cross-site tracking cookies. You can clear cookies through your browser settings, though doing so will sign you out of the service.',
  },
  children: {
    title: '7. Children’s Privacy',
    body: 'Yanay Tevet is not intended for children under the age of 13. We do not knowingly collect personal information from children. If you believe a child has provided us with personal data, please contact us and we will delete it.',
  },
  content: {
    title: '8. Your Content',
    body: 'All content you create on Yanay Tevet remains your property. We do not claim ownership over user-generated content.',
  },
  rights: {
    title: '9. Your Rights',
    body: 'You may request access to, correction of, or deletion of your personal data at any time by contacting us. We will respond in accordance with applicable data protection law.',
  },
  operator: {
    title: '10. Operator and Jurisdiction',
    body: 'Yanay Tevet is operated by an independent developer based in Israel. This Privacy Policy is governed by the laws of the State of Israel.',
  },
  changes: {
    title: '11. Changes to This Policy',
    body: 'We may update this Privacy Policy from time to time. We will notify you of significant changes by updating the date at the top of this page. Your continued use of the service after changes constitutes acceptance of the updated policy.',
  },
  contact: {
    title: '12. Contact Us',
    beforeEmail: 'If you have questions about this Privacy Policy or how your data is handled, please contact us at ',
    afterEmail: '.',
  },
};

export type PrivacyStrings = typeof en;
