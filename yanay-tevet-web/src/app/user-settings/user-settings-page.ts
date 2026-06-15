import {AfterViewInit, Component, computed, inject, signal} from '@angular/core';
import {SUPPORT_EMAIL} from '../common/constants/app-constants';
import {FormsModule} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';
import {BasePageComponent} from '../common/components/base-page-component';
import {LayoutHandle} from '../layout/layout-handle';
import {AuthenticationService} from '../common/authentication/authentication.service';
import {DialogService} from '../common/dialogs/dialogs.service';
import {FilesUploadService} from '../common/services/files-upload.service';
import {updateMyTimezoneView, updateMyUserView, uploadUserProfileImageView} from '../../generated-files/api/users';
import {changePasswordView} from '../../generated-files/auth';
import {interval} from 'rxjs';

interface TimezoneOption {
  name: string;
  label: string;
  offset: string;
}

@Component({
  selector: 'app-user-settings-page',
  imports: [FormsModule],
  providers: [LayoutHandle],
  templateUrl: './user-settings-page.html',
})
export class UserSettingsPage extends BasePageComponent implements AfterViewInit {
  private readonly layoutHandle = inject(LayoutHandle);
  private readonly route = inject(ActivatedRoute);
  readonly authService = inject(AuthenticationService);
  private readonly dialogService = inject(DialogService);
  private readonly filesUploadService = inject(FilesUploadService);

  readonly supportEmail = SUPPORT_EMAIL;
  readonly passkeysHighlighted = signal(false);

  readonly firstName = signal('');
  readonly lastName = signal('');
  readonly email = signal('');
  readonly oldPassword = signal('');
  readonly newPassword = signal('');
  readonly confirmNewPassword = signal('');
  readonly isSavingName = signal(false);
  readonly isChangingPassword = signal(false);
  readonly isUploadingImage = signal(false);
  readonly isDeletingPasskey = signal<number | null>(null);
  readonly isRegisteringPasskey = signal(false);

  readonly passwordChangedSuccess = signal(false);

  readonly browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  readonly tzSearch = signal('');
  readonly tzPanelOpen = signal(false);
  readonly isSavingTz = signal(false);
  private readonly now = signal(new Date());

  readonly allTimezones = computed<TimezoneOption[]>(() => {
    const names = this.supportedTimezones();
    const sample = new Date();
    return names.map(name => ({
      name,
      label: name.replace(/_/g, ' '),
      offset: this.getOffset(name, sample),
    }));
  });

  readonly filteredTimezones = computed<TimezoneOption[]>(() => {
    const term = this.tzSearch().trim().toLowerCase();
    const all = this.allTimezones();
    if (!term) {
      return all;
    }
    return all.filter(tz =>
      tz.label.toLowerCase().includes(term) || tz.offset.toLowerCase().includes(term));
  });

  readonly currentTimezone = computed<string | null>(() => this.authService.user()?.timezone ?? null);
  readonly effectiveTimezone = computed<string>(() => this.currentTimezone() ?? 'UTC');
  readonly currentTimezoneLabel = computed<string>(() => {
    const tz = this.currentTimezone();
    return tz ? tz.replace(/_/g, ' ') : 'UTC (default)';
  });
  readonly currentTimezoneOffset = computed<string>(() =>
    this.getOffset(this.effectiveTimezone(), this.now()));
  readonly currentLocalTime = computed<string>(() =>
    this.now().toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: this.effectiveTimezone(),
    }));
  readonly isBrowserTimezoneActive = computed<boolean>(() =>
    this.currentTimezone() === this.browserTimezone);
  readonly selectedById = computed<Record<string, boolean>>(() => {
    const current = this.currentTimezone();
    return Object.fromEntries(this.allTimezones().map(tz => [tz.name, tz.name === current]));
  });

  readonly passwordRules = computed(() => {
    const p = this.newPassword();
    return [
      {label: 'At least 8 characters', met: p.length >= 8},
      {label: 'An uppercase letter', met: /[A-Z]/.test(p)},
      {label: 'A lowercase letter', met: /[a-z]/.test(p)},
      {label: 'A digit', met: /\d/.test(p)},
    ];
  });

  readonly newPasswordValid = computed(() =>
    this.newPassword().length > 0 && this.passwordRules().every(r => r.met)
  );

  readonly passwordMismatch = computed(() =>
    this.newPassword().length > 0 &&
    this.confirmNewPassword().length > 0 &&
    this.newPassword() !== this.confirmNewPassword()
  );

  readonly hasUsablePassword = computed(() =>
    this.authService.user()?.has_usable_password ?? true
  );

  readonly canChangePassword = computed(() =>
    this.newPasswordValid() &&
    !this.passwordMismatch() &&
    (this.hasUsablePassword() ? this.oldPassword().length > 0 : true)
  );

  readonly canRegisterPasskey = computed(() =>
    (this.authService.credentials()?.credentials?.length ?? 0) < 3
  );

  constructor() {
    super();
    this.layoutHandle.registerBreadcrumb([{label: 'Account Settings'}]);
    const user = this.authService.user();
    if (user) {
      this.firstName.set(user.first_name);
      this.lastName.set(user.last_name);
      this.email.set(user.email ?? '');
    }
    this.subscriptions.push(
      interval(20000).subscribe(() => this.now.set(new Date())),
    );
  }

  toggleTzPanel(): void {
    this.tzPanelOpen.update(open => !open);
    if (!this.tzPanelOpen()) {
      this.tzSearch.set('');
    }
  }

  async selectTimezone(name: string): Promise<void> {
    await this.saveTimezone(name);
  }

  async useBrowserTimezone(): Promise<void> {
    await this.saveTimezone(this.browserTimezone);
  }

  private async saveTimezone(timezone: string): Promise<void> {
    if (this.isSavingTz()) {
      return;
    }
    this.isSavingTz.set(true);
    try {
      const result = await updateMyTimezoneView({body: {timezone}});
      if (result.error) {
        const err = result.error as {detail?: string};
        await this.dialogService.showNotificationDialog({
          title: 'Error',
          text: err?.detail ?? 'Failed to update timezone.',
        });
        return;
      }
      await this.authService.checkAuth();
      this.tzPanelOpen.set(false);
      this.tzSearch.set('');
    } catch (err: unknown) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: err instanceof Error ? err.message : 'Failed to update timezone',
      });
    } finally {
      this.isSavingTz.set(false);
    }
  }

  private supportedTimezones(): string[] {
    const intlWithValues = Intl as unknown as {supportedValuesOf?: (key: string) => string[]};
    const values = intlWithValues.supportedValuesOf?.('timeZone');
    if (values && values.length > 0) {
      return values;
    }
    return [this.browserTimezone, 'UTC'].filter(Boolean);
  }

  private getOffset(timezone: string, sample: Date): string {
    try {
      const parts = new Intl.DateTimeFormat('en-US', {
        timeZone: timezone,
        timeZoneName: 'shortOffset',
      }).formatToParts(sample);
      const name = parts.find(part => part.type === 'timeZoneName')?.value;
      return name ?? 'GMT';
    } catch {
      return 'GMT';
    }
  }

  ngAfterViewInit(): void {
    this.subscriptions.push(
      this.route.fragment.subscribe(fragment => {
        if (fragment === 'passkeys') {
          setTimeout(() => {
            document.getElementById('passkeys-section')?.scrollIntoView({behavior: 'smooth', block: 'start'});
            this.passkeysHighlighted.set(true);
            setTimeout(() => this.passkeysHighlighted.set(false), 1500);
          }, 100);
        }
      })
    );
  }

  async saveProfile(): Promise<void> {
    this.isSavingName.set(true);
    try {
      const result = await updateMyUserView({
        body: {first_name: this.firstName(), last_name: this.lastName(), email: this.email().trim() || null},
      });
      if (result.error) {
        const err = result.error as {detail?: string};
        await this.dialogService.showNotificationDialog({
          title: 'Error',
          text: err?.detail ?? 'Failed to save changes.',
        });
        return;
      }
      await this.authService.checkAuth();
    } catch (err: unknown) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: err instanceof Error ? err.message : 'Failed to save changes',
      });
    } finally {
      this.isSavingName.set(false);
    }
  }

  async changePassword(): Promise<void> {
    if (!this.canChangePassword()) {
      return;
    }
    this.isChangingPassword.set(true);
    this.passwordChangedSuccess.set(false);
    try {
      const result = await changePasswordView({
        body: {old_password: this.oldPassword(), new_password: this.newPassword()},
      });
      if (result.error) {
        await this.dialogService.showNotificationDialog({
          title: 'Error',
          text: 'Old password is incorrect',
        });
        return;
      }
      this.oldPassword.set('');
      this.newPassword.set('');
      this.confirmNewPassword.set('');
      await this.authService.checkAuth();
      this.passwordChangedSuccess.set(true);
      setTimeout(() => this.passwordChangedSuccess.set(false), 4000);
    } catch (err: unknown) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: err instanceof Error ? err.message : 'Failed to change password',
      });
    } finally {
      this.isChangingPassword.set(false);
    }
  }

  async uploadProfileImage(): Promise<void> {
    this.isUploadingImage.set(true);
    try {
      await this.filesUploadService.uploadFile('image/*', async (files: File[]) => {
        const res = await uploadUserProfileImageView({
          body: {files},
        });
        return res?.data;
      });
      await this.authService.checkAuth();
    } catch (err: unknown) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: err instanceof Error ? err.message : 'Failed to upload image',
      });
    } finally {
      this.isUploadingImage.set(false);
    }
  }

  async registerPasskey(): Promise<void> {
    this.isRegisteringPasskey.set(true);
    try {
      await this.authService.registerPasskey();
    } catch (err: unknown) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: err instanceof Error ? err.message : 'Failed to register passkey',
      });
    } finally {
      this.isRegisteringPasskey.set(false);
    }
  }

  async deletePasskey(credentialId: string, passkeyDbId: number): Promise<void> {
    this.isDeletingPasskey.set(passkeyDbId);
    try {
      await this.authService.deleteCredential(credentialId);
    } catch (err: unknown) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: err instanceof Error ? err.message : 'Failed to remove passkey',
      });
    } finally {
      this.isDeletingPasskey.set(null);
    }
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString();
  }
}
