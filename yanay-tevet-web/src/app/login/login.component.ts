import {Component, inject, OnInit, signal} from '@angular/core';
import {ActivatedRoute, Router, RouterLink} from '@angular/router';
import {RoutingService} from '../shared/services/routing.service';
import {AuthenticationService} from '../common/authentication/authentication.service';
import {WebAuthnAuthService} from '../common/services/webauthn-auth.service';
import {GoogleAuthService} from '../common/services/google-auth.service';
import {injectStrings} from '../shared/i18n/strings';
import {LOGIN_STRINGS} from './i18n';
import {LoginError} from './i18n/en';

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
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  protected readonly t = injectStrings(LOGIN_STRINGS);

  readonly username = signal('');
  readonly password = signal('');
  readonly showPassword = signal(false);
  readonly error = signal<LoginError | null>(null);
  readonly usernameFocused = signal(false);
  readonly passwordFocused = signal(false);
  readonly passkeySupported = signal(false);
  readonly isPasskeyLoading = signal(false);
  readonly passkeyFailed = signal(false);
  readonly isGoogleLoading = signal(false);

  async ngOnInit() {
    this.passkeySupported.set(await this.webAuthnService.isPasskeySupported());
  }

  private navigateAfterLogin(): Promise<boolean> {
    const redirect = this.route.snapshot.queryParamMap.get('redirect');
    if (redirect) {
      return this.router.navigateByUrl(redirect);
    }
    return this.routingService.navigateToHome();
  }

  async onGoogleLogin() {
    this.isGoogleLoading.set(true);
    this.error.set(null);
    try {
      const code = await this.googleAuthService.signIn();
      await this.authService.loginWithGoogle(code);
      if (this.authService.isLoggedIn()) {
        await this.navigateAfterLogin();
      } else {
        this.error.set('googleFailed');
      }
    } catch {
      this.error.set('googleFailed');
    } finally {
      this.isGoogleLoading.set(false);
    }
  }

  togglePassword() {
    this.showPassword.update(v => !v);
  }

  async onSubmit() {
    if (!this.username().trim() || !this.password().trim()) {
      this.error.set('missingCredentials');
      return;
    }
    this.error.set(null);
    await this.authService.tryLogin(this.username(), this.password());
    if (this.authService.isLoggedIn()) {
      await this.navigateAfterLogin();
    } else {
      this.error.set('incorrectCredentials');
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
        await this.navigateAfterLogin();
      }
    } catch {
      this.passkeyFailed.set(true);
    } finally {
      this.isPasskeyLoading.set(false);
    }
  }
}
