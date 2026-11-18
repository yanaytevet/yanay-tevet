import {Component, computed, inject, signal} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {joinSpecialDateCalendarView} from '../../../generated-files/api/special-dates';
import {
  getSpecialDateCalendarJoinPreviewView,
  SpecialDateCalendarJoinPreviewSchema,
} from '../../../generated-files/api/special-dates-public';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {ErrorStateComponent} from '../../common/components/page/error-state/error-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {HUB_APPS} from '../../shared/apps/hub-apps';
import {LanguageService} from '../../shared/i18n/language.service';
import {fill, injectStrings, plural} from '../../shared/i18n/strings';
import {SPECIAL_DATES_STRINGS} from '../i18n';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-join-calendar',
  standalone: true,
  imports: [NgIcon, LoadingStateComponent, ErrorStateComponent],
  templateUrl: './join-calendar.component.html',
})
export class JoinCalendarComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly routingService = inject(RoutingService);
  readonly authService = inject(AuthenticationService);
  private readonly language = inject(LanguageService).language;
  protected readonly t = injectStrings(SPECIAL_DATES_STRINGS);

  private readonly token = this.route.snapshot.paramMap.get('token') ?? '';

  protected readonly appIcon = HUB_APPS.dates.icon;

  readonly preview = signal<SpecialDateCalendarJoinPreviewSchema | null>(null);
  readonly isLoading = signal<boolean>(true);
  readonly isInvalid = signal<boolean>(false);
  readonly isJoining = signal<boolean>(false);
  readonly errorMessage = signal<string>('');

  readonly isAuthKnown = computed(() => this.authService.isLoggedIn() !== null);
  readonly isLoggedIn = computed(() => this.authService.isLoggedIn() === true);
  readonly summary = computed(() => {
    const preview = this.preview();
    if (!preview) {
      return '';
    }
    const language = this.language();
    const t = this.t();
    return `${plural(language, preview.event_count, t.eventsCount)} · ${plural(language, preview.member_count, t.membersCount)}`;
  });
  readonly invitesYouText = computed(() => fill(this.t().join.invitesYou, {name: this.preview()?.owner_name ?? ''}));

  constructor() {
    void this.loadPreview();
  }

  private async loadPreview(): Promise<void> {
    try {
      const res = await getSpecialDateCalendarJoinPreviewView({query: {token: this.token}});
      if (res.error) {
        this.isInvalid.set(true);
        return;
      }
      this.preview.set(res.data);
    } finally {
      this.isLoading.set(false);
    }
  }

  async loginAndJoin(): Promise<void> {
    await this.router.navigate(['/login'], {queryParams: {redirect: this.router.url}});
  }

  async join(): Promise<void> {
    if (this.isJoining()) {
      return;
    }
    this.isJoining.set(true);
    this.errorMessage.set('');
    try {
      const res = await joinSpecialDateCalendarView({body: {token: this.token}});
      if (res.error) {
        const err = res.error as {detail?: string};
        this.errorMessage.set(err?.detail || this.t().join.joinFailed);
        return;
      }
      await this.routingService.navigateToSpecialDates(res.data.id);
    } finally {
      this.isJoining.set(false);
    }
  }
}
