import {Component, computed, inject, OnInit, signal} from '@angular/core';
import {RouterLink, RouterLinkActive} from '@angular/router';
import {RoutingService} from '../../shared/services/routing.service';
import {bootstrapMoonFill, bootstrapSunFill, bootstrapPeople} from '@ng-icons/bootstrap-icons';
import {featherChevronRight} from '@ng-icons/feather-icons';
import {NgIcon} from '@ng-icons/core';
import {DarkModeService} from '../../common/services/dark-mode.service';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {LayoutService} from '../layout-service';
import {HUB_APPS} from '../../shared/apps/hub-apps';

@Component({
  selector: 'app-navigation-left-drawer',
  standalone: true,
  imports: [
    RouterLink,
    RouterLinkActive,
    NgIcon,
  ],
  templateUrl: './app-navigation-left-drawer.component.html',
  styleUrl: './app-navigation-left-drawer.component.css',
})
export class AppNavigationLeftDrawer implements OnInit {
  public authService = inject(AuthenticationService);
  public routingService = inject(RoutingService);
  public darkModeService = inject(DarkModeService);
  public layoutService = inject(LayoutService);

  protected readonly apps = HUB_APPS;
  protected readonly homeUrl = this.routingService.getHomeUrl();
  protected readonly genreTrainerUrl = this.routingService.getGenreTrainerUrl();
  protected readonly japaneseUrl = this.routingService.getJapaneseHomeUrl();
  protected readonly japaneseIngestUrl = this.routingService.getJapaneseIngestUrl();
  protected readonly japaneseReviewUrl = this.routingService.getJapaneseReviewUrl();
  protected readonly specialDatesUrl = this.routingService.getSpecialDatesUrl();
  protected readonly dreamDiaryUrl = this.routingService.getDreamDiaryUrl();
  protected readonly apartmentHuntUrl = this.routingService.getApartmentHuntUrl();
  protected readonly villaVillekullaUrl = this.routingService.getVillaVillekullaUrl();
  protected readonly rentersCrmUrl = this.routingService.getRentersCrmUrl();
  protected readonly itineraryListsUrl = this.routingService.getItineraryListsUrl();
  protected readonly shoppingListsUrl = this.routingService.getShoppingListsUrl();
  protected readonly taskManagementUrl = this.routingService.getTaskManagementUrl();
  protected readonly workoutPlanUrl = this.routingService.getWorkoutPlanUrl();
  protected readonly myDashboardUrl = this.routingService.getMyDashboardUrl();
  protected readonly adminUsersUrl = this.routingService.getAdminUsersUrl();
  protected readonly userSettingsUrl = this.routingService.getUserSettingsUrl();
  protected readonly faqUrl = this.routingService.getFaqUrl();
  protected readonly contactUrl = this.routingService.getContactUrl();

  public readonly hasApartmentHunt = computed(() => this.authService.hasPermission('apartment_hunt'));
  public readonly hasRentersCrm = computed(() => this.authService.hasPermission('renters_crm'));
  public readonly hasVillaVillekulla = computed(() => this.authService.hasPermission('villa_villekulla'));
  public readonly hasHomeSweetHome = computed(
    () => this.hasApartmentHunt() || this.hasRentersCrm() || this.hasVillaVillekulla(),
  );
  public readonly homeSweetHomeUrl = computed(() => {
    if (this.hasApartmentHunt()) {
      return this.routingService.getApartmentHuntUrl();
    }
    if (this.hasVillaVillekulla()) {
      return this.routingService.getVillaVillekullaUrl();
    }
    return this.routingService.getRentersCrmUrl();
  });
  public readonly hasItineraryLists = computed(() => this.authService.hasPermission('itinerary_lists'));
  public readonly hasShoppingLists = computed(() => this.authService.hasPermission('shopping_lists'));
  public readonly hasTaskManagement = computed(() => this.authService.hasPermission('task_management'));
  public readonly hasWorkoutPlan = computed(() => this.authService.hasPermission('workout_plan'));

  private readonly ABOUT_FOLDED_KEY = 'about_folded';
  public isAboutFolded = signal<boolean>(localStorage.getItem(this.ABOUT_FOLDED_KEY) !== 'false');

  async ngOnInit() {
    if (this.authService.isLoggedIn()) {
      await this.authService.loadCredentials();
    }
  }

  async logout() {
    await this.authService.logout();
    this.layoutService.closeBothDrawers();
  }

  toggleAboutFold() {
    this.isAboutFolded.update(folded => {
      const newVal = !folded;
      localStorage.setItem(this.ABOUT_FOLDED_KEY, newVal.toString());
      return newVal;
    });
  }

  protected readonly bootstrapMoonFill = bootstrapMoonFill;
  protected readonly bootstrapSunFill = bootstrapSunFill;
  protected readonly featherChevronRight = featherChevronRight;
  protected readonly bootstrapPeople = bootstrapPeople;
}
