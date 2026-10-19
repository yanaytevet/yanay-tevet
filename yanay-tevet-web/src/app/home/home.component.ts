import {Component, computed, inject} from '@angular/core';
import {RouterLink} from '@angular/router';
import {bootstrapPeople} from '@ng-icons/bootstrap-icons';
import {RoutingService} from '../shared/services/routing.service';
import {BasePageComponent} from '../common/components/base-page-component';
import {AuthenticationService} from '../common/authentication/authentication.service';
import {HUB_APPS} from '../shared/apps/hub-apps';
import {HubTileApp, HubTileComponent} from './hub-tile/hub-tile.component';

@Component({
  selector: 'app-home',
  imports: [RouterLink, HubTileComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent extends BasePageComponent {
  readonly routingService = inject(RoutingService);
  readonly authService = inject(AuthenticationService);

  protected readonly apps = HUB_APPS;
  protected readonly userManagementApp: HubTileApp = {name: 'User Management', icon: bootstrapPeople, key: null};

  protected readonly genreTrainerUrl = this.routingService.getGenreTrainerUrl();
  protected readonly japaneseUrl = this.routingService.getJapaneseHomeUrl();
  protected readonly specialDatesUrl = this.routingService.getSpecialDatesUrl();
  protected readonly dreamDiaryUrl = this.routingService.getDreamDiaryUrl();
  protected readonly itineraryListsUrl = this.routingService.getItineraryListsUrl();
  protected readonly shoppingListsUrl = this.routingService.getShoppingListsUrl();
  protected readonly taskManagementUrl = this.routingService.getTaskManagementUrl();
  protected readonly workoutPlanUrl = this.routingService.getWorkoutPlanUrl();
  protected readonly myDashboardUrl = this.routingService.getMyDashboardUrl();
  protected readonly adminUsersUrl = this.routingService.getAdminUsersUrl();
  protected readonly faqUrl = this.routingService.getFaqUrl();
  protected readonly contactUrl = this.routingService.getContactUrl();
  protected readonly privacyUrl = this.routingService.getPrivacyUrl();
  protected readonly termsUrl = this.routingService.getTermsUrl();

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
  readonly hasShoppingLists = computed(() => this.authService.hasPermission('shopping_lists'));
  readonly hasTaskManagement = computed(() => this.authService.hasPermission('task_management'));
  readonly hasWorkoutPlan = computed(() => this.authService.hasPermission('workout_plan'));
  readonly hasAnyPrivateApp = computed(() =>
    this.hasDreamDiary() || this.hasHomeSweetHome() || this.hasItineraryLists() || this.hasShoppingLists()
    || this.hasTaskManagement() || this.hasWorkoutPlan()
  );
}
