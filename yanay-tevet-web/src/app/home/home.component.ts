import {Component, computed, inject} from '@angular/core';
import {RoutingService} from '../shared/services/routing.service';
import {BasePageComponent} from '../common/components/base-page-component';
import {RouterLink} from '@angular/router';
import {AuthenticationService} from '../common/authentication/authentication.service';

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent extends BasePageComponent {
  readonly routingService = inject(RoutingService);
  readonly authService = inject(AuthenticationService);

  readonly hasDreamDiary = computed(() => this.authService.hasPermission('dream_diary'));
  readonly hasApartmentHunt = computed(() => this.authService.hasPermission('apartment_hunt'));
  readonly hasItineraryLists = computed(() => this.authService.hasPermission('itinerary_lists'));
}
