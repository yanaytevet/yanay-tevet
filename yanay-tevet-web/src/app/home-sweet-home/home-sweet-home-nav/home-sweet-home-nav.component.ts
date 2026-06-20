import {Component, computed, inject} from '@angular/core';
import {RouterLink, RouterLinkActive} from '@angular/router';
import {RoutingService} from '../../shared/services/routing.service';
import {AuthenticationService} from '../../common/authentication/authentication.service';

@Component({
  selector: 'app-home-sweet-home-nav',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './home-sweet-home-nav.component.html',
})
export class HomeSweetHomeNavComponent {
  protected readonly routingService = inject(RoutingService);
  private readonly authService = inject(AuthenticationService);

  protected readonly hasApartmentHunt = computed(() => this.authService.hasPermission('apartment_hunt'));
  protected readonly hasVillaVillekulla = computed(() => this.authService.hasPermission('villa_villekulla'));
  protected readonly hasRentersCrm = computed(() => this.authService.hasPermission('renters_crm'));
}
