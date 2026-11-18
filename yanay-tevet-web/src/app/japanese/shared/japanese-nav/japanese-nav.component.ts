import {Component, computed, inject} from '@angular/core';
import {AuthenticationService} from '../../../common/authentication/authentication.service';
import {RoutingService} from '../../../shared/services/routing.service';
import {SubNavComponent, SubNavLink} from '../../../common/components/page/sub-nav/sub-nav.component';
import {injectStrings} from '../../../shared/i18n/strings';
import {JAPANESE_STRINGS} from '../../i18n';

@Component({
  selector: 'app-japanese-nav',
  standalone: true,
  imports: [SubNavComponent],
  templateUrl: './japanese-nav.component.html',
})
export class JapaneseNavComponent {
  private readonly authService = inject(AuthenticationService);
  private readonly routingService = inject(RoutingService);
  private readonly t = injectStrings(JAPANESE_STRINGS);

  protected readonly links = computed<SubNavLink[]>(() => {
    const nav = this.t().nav;
    const links: SubNavLink[] = [{label: nav.explore, url: this.routingService.getJapaneseHomeUrl(), exact: true}];
    if (this.authService.user()?.is_admin) {
      links.push({label: nav.ingest, url: this.routingService.getJapaneseIngestUrl()});
      links.push({label: nav.review, url: this.routingService.getJapaneseReviewUrl()});
    }
    return links;
  });
}
