// Strings for the page where a user approves the Claude connector. This file is the contract: every other
// language's file is typed against it. Names and hosts sit between a `…Before` and an `…After` string.
export const en = {
  invalidTitle: 'Invalid request',
  invalidBody: 'This authorization link is invalid or has expired. Please start again from Claude’s Connectors settings.',
  title: 'Connect to Claude',
  anApp: 'An app',
  wantsToConnectBefore: '',
  wantsToConnectAfter: ' wants to connect to your account. This will let Claude view and change your tasks, shopping lists and workout plans on your behalf — including projects, lists and plans shared with you.',
  signedInAsBefore: 'Signed in as ',
  signedInAsAfter: '',
  accessGrantedBefore: 'Access will be granted to ',
  accessGrantedAfter: '',
  deny: 'Deny',
  allow: 'Allow',
  redirecting: 'Redirecting…',
  loading: 'Loading…',
};

export type ConnectClaudeStrings = typeof en;
