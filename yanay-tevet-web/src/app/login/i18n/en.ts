// Strings for the sign-in page. This file is the contract: every other language's file is typed against it.
export const en = {
  appName: 'Yanay Tevet',
  subtitle: 'Sign in to your account',
  signingIn: 'Signing in…',
  continueWithGoogle: 'Continue with Google',
  registerNote: 'Google is currently the only way to create an account. Email and other options are coming soon.',
  orSignInWithPassword: 'or sign in with password',
  username: 'Username',
  usernamePlaceholder: 'your_username',
  password: 'Password',
  showPassword: 'Show password',
  hidePassword: 'Hide password',
  signIn: 'Sign in',
  or: 'or',
  authenticating: 'Authenticating…',
  signInWithPasskey: 'Sign in with Passkey',
  errors: {
    googleFailed: 'Google sign-in failed. Please try again.',
    missingCredentials: 'Please enter your username and password.',
    incorrectCredentials: 'Incorrect username or password. Please try again.',
    passkeyFailed: 'Passkey sign-in failed — please use your password.',
  },
};

export type LoginStrings = typeof en;
export type LoginError = keyof LoginStrings['errors'];
