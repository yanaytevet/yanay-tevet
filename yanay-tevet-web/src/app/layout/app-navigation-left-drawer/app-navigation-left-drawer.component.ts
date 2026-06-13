import {Component, computed, inject, OnInit, signal} from '@angular/core';
import {RouterLink, RouterLinkActive} from '@angular/router';
import {RoutingService} from '../../shared/services/routing.service';
import {
  bootstrapMoonFill,
  bootstrapSunFill,
  bootstrapChevronRight
} from '@ng-icons/bootstrap-icons';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {DarkModeService} from '../../common/services/dark-mode.service';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {LayoutService} from '../layout-service';

@Component({
  selector: 'app-navigation-left-drawer',
  standalone: true,
  imports: [
    RouterLink,
    RouterLinkActive,
    NgIcon,
  ],
  providers: [provideIcons({bootstrapMoonFill, bootstrapSunFill, bootstrapChevronRight})],
  templateUrl: './app-navigation-left-drawer.component.html',
  styleUrl: './app-navigation-left-drawer.component.css',
})
export class AppNavigationLeftDrawer implements OnInit {
  public authService = inject(AuthenticationService);
  public routingService = inject(RoutingService);
  public darkModeService = inject(DarkModeService);
  public layoutService = inject(LayoutService);

  public readonly hasApartmentHunt = computed(() => this.authService.hasPermission('apartment_hunt'));
  public readonly hasItineraryLists = computed(() => this.authService.hasPermission('itinerary_lists'));
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
  protected readonly bootstrapChevronRight = bootstrapChevronRight;
}
