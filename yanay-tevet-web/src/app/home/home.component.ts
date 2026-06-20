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
  readonly hasRentersCrm = computed(() => this.authService.hasPermission('renters_crm'));
  readonly hasVillaVillekulla = computed(() => this.authService.hasPermission('villa_villekulla'));
  readonly hasHomeSweetHome = computed(
    () => this.hasApartmentHunt() || this.hasRentersCrm() || this.hasVillaVillekulla(),
  );
  readonly homeSweetHomeUrl = computed(() => {
    if (this.hasApartmentHunt()) {
      return this.routingService.getApartmentHuntUrl();
    }
    if (this.hasVillaVillekulla()) {
      return this.routingService.getVillaVillekullaUrl();
    }
    return this.routingService.getRentersCrmUrl();
  });
  readonly hasItineraryLists = computed(() => this.authService.hasPermission('itinerary_lists'));
  readonly hasTaskManagement = computed(() => this.authService.hasPermission('task_management'));
  readonly hasWorkoutPlan = computed(() => this.authService.hasPermission('workout_plan'));
}
