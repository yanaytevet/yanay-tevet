import {Component, computed, inject, signal} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {joinSpecialDateCalendarView} from '../../../generated-files/api/special-dates';
import {
  getSpecialDateCalendarJoinPreviewView,
  SpecialDateCalendarJoinPreviewSchema,
} from '../../../generated-files/api/special-dates-public';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-join-calendar',
  standalone: true,
  templateUrl: './join-calendar.component.html',
})
export class JoinCalendarComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly routingService = inject(RoutingService);
  readonly authService = inject(AuthenticationService);

  private readonly token = this.route.snapshot.paramMap.get('token') ?? '';

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
    const members = preview.member_count === 1 ? 'חבר/ה אחד/ת' : `${preview.member_count} חברים`;
    return `${preview.event_count} אירועים · ${members}`;
  });

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
        this.errorMessage.set(err?.detail || 'ההצטרפות נכשלה, נסו שוב.');
        return;
      }
      await this.routingService.navigateToSpecialDates(res.data.id);
    } finally {
      this.isJoining.set(false);
    }
  }
}
