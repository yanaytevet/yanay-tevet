import {Component, inject, OnInit, signal} from '@angular/core';
import {RouterLink} from '@angular/router';
import {RoutingService} from '../shared/services/routing.service';
import {AuthenticationService} from '../common/authentication/authentication.service';
import {WebAuthnAuthService} from '../common/services/webauthn-auth.service';
import {GoogleAuthService} from '../common/services/google-auth.service';

@Component({
  selector: 'app-login',
  imports: [RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent implements OnInit {
  private authService = inject(AuthenticationService);
  private routingService = inject(RoutingService);
  private webAuthnService = inject(WebAuthnAuthService);
  private googleAuthService = inject(GoogleAuthService);

  readonly username = signal('');
  readonly password = signal('');
  readonly showPassword = signal(false);
  readonly error = signal('');
  readonly usernameFocused = signal(false);
  readonly passwordFocused = signal(false);
  readonly passkeySupported = signal(false);
  readonly isPasskeyLoading = signal(false);
  readonly passkeyFailed = signal(false);
  readonly isGoogleLoading = signal(false);

  async ngOnInit() {
    this.passkeySupported.set(await this.webAuthnService.isPasskeySupported());
  }

  async onGoogleLogin() {
    this.isGoogleLoading.set(true);
    this.error.set('');
    try {
      const code = await this.googleAuthService.signIn();
      await this.authService.loginWithGoogle(code);
      if (this.authService.isLoggedIn()) {
        await this.routingService.navigateToHome();
      } else {
        this.error.set('Google sign-in failed. Please try again.');
      }
    } catch {
      this.error.set('Google sign-in failed. Please try again.');
    } finally {
      this.isGoogleLoading.set(false);
    }
  }

  togglePassword() {
    this.showPassword.update(v => !v);
  }

  async onSubmit() {
    if (!this.username().trim() || !this.password().trim()) {
      this.error.set('Please enter your username and password.');
      return;
    }
    this.error.set('');
    await this.authService.tryLogin(this.username(), this.password());
    if (this.authService.isLoggedIn()) {
      await this.routingService.navigateToHome();
    } else {
      this.error.set('Incorrect username or password. Please try again.');
    }
  }

  onPasswordKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      this.onSubmit();
    }
  }

  async tryPasskeyLogin() {
    this.isPasskeyLoading.set(true);
    this.passkeyFailed.set(false);
    try {
      await this.authService.loginWithPasskey();
      if (this.authService.isLoggedIn()) {
        await this.routingService.navigateToHome();
      }
    } catch {
      this.passkeyFailed.set(true);
    } finally {
      this.isPasskeyLoading.set(false);
    }
  }
}
