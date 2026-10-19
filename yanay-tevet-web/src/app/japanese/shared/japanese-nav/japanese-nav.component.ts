import {Component, computed, inject} from '@angular/core';
import {AuthenticationService} from '../../../common/authentication/authentication.service';
import {RoutingService} from '../../../shared/services/routing.service';
import {SubNavComponent, SubNavLink} from '../../../common/components/page/sub-nav/sub-nav.component';

@Component({
  selector: 'app-japanese-nav',
  standalone: true,
  imports: [SubNavComponent],
  templateUrl: './japanese-nav.component.html',
})
export class JapaneseNavComponent {
  private readonly authService = inject(AuthenticationService);
  private readonly routingService = inject(RoutingService);

  protected readonly links = computed<SubNavLink[]>(() => {
    const links: SubNavLink[] = [{label: 'Explore', url: this.routingService.getJapaneseHomeUrl(), exact: true}];
    if (this.authService.user()?.is_admin) {
      links.push({label: 'Ingest', url: this.routingService.getJapaneseIngestUrl()});
      links.push({label: 'Review', url: this.routingService.getJapaneseReviewUrl()});
    }
    return links;
  });
}
