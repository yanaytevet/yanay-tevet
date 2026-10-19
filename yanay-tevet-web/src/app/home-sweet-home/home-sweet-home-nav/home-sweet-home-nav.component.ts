import {Component, computed, inject} from '@angular/core';
import {RoutingService} from '../../shared/services/routing.service';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {SubNavComponent, SubNavLink} from '../../common/components/page/sub-nav/sub-nav.component';

@Component({
  selector: 'app-home-sweet-home-nav',
  standalone: true,
  imports: [SubNavComponent],
  templateUrl: './home-sweet-home-nav.component.html',
})
export class HomeSweetHomeNavComponent {
  private readonly routingService = inject(RoutingService);
  private readonly authService = inject(AuthenticationService);

  protected readonly links = computed<SubNavLink[]>(() => {
    const links: SubNavLink[] = [];
    if (this.authService.hasPermission('apartment_hunt')) {
      links.push({label: 'Apartment Hunt', url: this.routingService.getApartmentHuntUrl()});
    }
    if (this.authService.hasPermission('villa_villekulla')) {
      links.push({label: 'Villa Villekulla', url: this.routingService.getVillaVillekullaUrl()});
    }
    if (this.authService.hasPermission('renters_crm')) {
      links.push({label: 'Renters CRM', url: this.routingService.getRentersCrmUrl()});
    }
    return links;
  });
}
