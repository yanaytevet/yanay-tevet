import {Component, computed, inject} from '@angular/core';
import {RoutingService} from '../../shared/services/routing.service';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {SubNavComponent, SubNavLink} from '../../common/components/page/sub-nav/sub-nav.component';
import {injectStrings} from '../../shared/i18n/strings';
import {HOME_SWEET_HOME_STRINGS} from '../i18n';

@Component({
  selector: 'app-home-sweet-home-nav',
  standalone: true,
  imports: [SubNavComponent],
  templateUrl: './home-sweet-home-nav.component.html',
})
export class HomeSweetHomeNavComponent {
  private readonly routingService = inject(RoutingService);
  private readonly authService = inject(AuthenticationService);
  protected readonly t = injectStrings(HOME_SWEET_HOME_STRINGS);

  protected readonly links = computed<SubNavLink[]>(() => {
    const t = this.t().nav;
    const links: SubNavLink[] = [];
    if (this.authService.hasPermission('apartment_hunt')) {
      links.push({label: t.apartmentHunt, url: this.routingService.getApartmentHuntUrl()});
    }
    if (this.authService.hasPermission('villa_villekulla')) {
      links.push({label: t.villaVillekulla, url: this.routingService.getVillaVillekullaUrl()});
    }
    if (this.authService.hasPermission('renters_crm')) {
      links.push({label: t.rentersCrm, url: this.routingService.getRentersCrmUrl()});
    }
    return links;
  });
}
