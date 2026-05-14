import {computed, inject, Injectable, signal} from '@angular/core';
import {AuthSchema, authView, loginView, logoutView, Permissions, UserSchema} from '../../../generated-files/auth';
import {googleLoginView} from '../../../generated-files/auth';
import {CredentialsSchema} from '../../../generated-files/auth';
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

  async tryLogin(username: string, password: string) {
    const {data} = await loginView({body: {username, password}});
    this.auth.set(data);
  }

  async loginWithGoogle(googleCode: string) {
    const {data} = await googleLoginView({body: {google_code: googleCode}});
    this.auth.set(data);
  }

  async loginWithPasskey(): Promise<void> {
    const data = await this.webAuthnService.loginWithPasskey();
    this.auth.set(data);
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
