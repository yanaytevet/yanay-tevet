import {computed, inject, Injectable, signal} from '@angular/core';
import {AuthSchema, authView, loginView, logoutView, Permissions, UserSchema} from '../../../generated-files/auth';
import {googleLoginView} from '../../../generated-files/auth';
import {CredentialsSchema} from '../../../generated-files/auth';
import {updateMyTimezoneView} from '../../../generated-files/api/users';
import {toObservable} from '@angular/core/rxjs-interop';
import {Router} from '@angular/router';
import {WebAuthnAuthService} from '../services/webauthn-auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
  auth = signal<AuthSchema>(null);
  auth$ = toObservable(this.auth);
  credentials = signal<CredentialsSchema | null>(null);

  user = computed<UserSchema>(() => this.auth()?.user ?? null);
  isLoggedIn = computed<boolean>(() => this.auth()?.is_authenticated ?? null);
  accessToken = computed<string>(() => this.auth()?.access_token ?? null);
  userInitials = computed<string>(() => this.user()?.initials?.toUpperCase() ?? null);

  hasPermission(permission: Permissions): boolean {
    const u = this.user();
    return u?.is_admin || u?.permissions?.includes(permission) || false;
  }

  private router = inject(Router);
  private webAuthnService = inject(WebAuthnAuthService);

  private refreshInFlight: Promise<void> | null = null;

  // The access token lives 15 minutes, and an API call renews it only after a 401. A websocket
  // subscribe carries the token inside its frame and is refused silently once it has expired, so the
  // socket asks for a token here, which is renewed first when it is about to run out.
  async freshAccessToken(): Promise<string | null> {
    const token = this.accessToken();
    if (!token || !this.expiresWithinAMinute(token)) {
      return token;
    }
    this.refreshInFlight ??= this.checkAuth().finally(() => {
      this.refreshInFlight = null;
    });
    await this.refreshInFlight;
    return this.accessToken();
  }

  private expiresWithinAMinute(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
      return payload.exp * 1000 - Date.now() < 60 * 1000;
    } catch {
      return true;
    }
  }

  async tryLogin(username: string, password: string) {
    const {data} = await loginView({body: {username, password}});
    this.auth.set(data);
    await this.ensureTimezone();
  }

  async loginWithGoogle(googleCode: string) {
    const {data} = await googleLoginView({body: {google_code: googleCode}});
    this.auth.set(data);
    await this.ensureTimezone();
  }

  async loginWithPasskey(): Promise<void> {
    const data = await this.webAuthnService.loginWithPasskey();
    this.auth.set(data);
    await this.ensureTimezone();
  }

  async registerPasskey(): Promise<void> {
    const data = await this.webAuthnService.registerPasskey();
    this.auth.set(data);
    await this.loadCredentials();
  }

  async loadCredentials(): Promise<void> {
    try {
      const creds = await this.webAuthnService.getCredentials();
      this.credentials.set(creds);
    } catch {
      this.credentials.set(null);
    }
  }

  async deleteCredential(credentialId: string): Promise<void> {
    await this.webAuthnService.deleteCredential(credentialId);
    await this.loadCredentials();
  }

  async logout() {
    await logoutView();
    this.credentials.set(null);
    await this.checkAuth();
    if (!this.isLoggedIn()) {
      await this.navigateToLogin();
    }
  }

  navigateToLogin(): Promise<boolean> {
    return this.router.navigateByUrl(this.router.createUrlTree(['/login']));
  }

  async checkAuth() {
    const res = await authView();
    this.auth.set(res.data);
    await this.ensureTimezone();
  }

  // On first login the user has no timezone — adopt the browser's so repeating
  // tasks reset at the right local 4 AM. Best-effort: never block auth on failure.
  async ensureTimezone(): Promise<void> {
    const user = this.user();
    if (!this.isLoggedIn() || !user || user.timezone) {
      return;
    }
    const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (!browserTimezone) {
      return;
    }
    try {
      const {data} = await updateMyTimezoneView({body: {timezone: browserTimezone}});
      if (data) {
        this.auth.update(auth => (auth ? {...auth, user: data} : auth));
      }
    } catch {
      // Timezone is non-critical; leave it unset and try again next session.
    }
  }

  async waitForAuth() {
    await new Promise(resolve => {
      this.auth$.subscribe((auth: AuthSchema) => {
        if (auth) {
          resolve(null);
        }
      });
    });
  }
}
