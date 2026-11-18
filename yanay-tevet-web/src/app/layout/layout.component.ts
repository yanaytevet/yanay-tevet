import {Component, effect, inject, viewChild, ViewContainerRef} from '@angular/core';
import {RouterLink, RouterLinkActive, RouterOutlet} from '@angular/router';
import {RoutingService} from '../shared/services/routing.service';
import {bootstrapArrowLeft, bootstrapList, bootstrapQuestionCircle} from '@ng-icons/bootstrap-icons';
import {NgIcon} from '@ng-icons/core';
import {featherChevronRight} from '@ng-icons/feather-icons';
import {AuthenticationService} from '../common/authentication/authentication.service';
import {LayoutService} from './layout-service';
import {AppNavigationLeftDrawer} from './app-navigation-left-drawer/app-navigation-left-drawer.component';
import {AppFooterComponent} from './app-footer/app-footer.component';
import {NgClass} from '@angular/common';
import {BreadcrumbComponent} from './breadcrumb/breadcrumb.component';
import {CHROME_STRINGS} from '../shared/i18n/chrome';
import {injectStrings} from '../shared/i18n/strings';
import {COMMON_STRINGS} from '../common/i18n';

@Component({
  selector: 'app-layout',
  imports: [
    RouterLink,
    RouterLinkActive,
    RouterOutlet,
    NgIcon,
    AppNavigationLeftDrawer,
    NgClass,
    AppFooterComponent,
    BreadcrumbComponent,
  ],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.css'
})
export class LayoutComponent {
  public authService = inject(AuthenticationService);
  public routingService = inject(RoutingService);
  public layoutService = inject(LayoutService);
  protected readonly t = injectStrings(CHROME_STRINGS);
  protected readonly common = injectStrings(COMMON_STRINGS);

  private readonly drawerHost = viewChild('drawerHost', {
    read: ViewContainerRef,
  });

  readonly updateDrawerEffect = effect(() => {
    const rightDrawerComponent = this.layoutService.rightDrawerComponent();
    const host = this.drawerHost();

    if (!host) return;

    host.clear();
    if (rightDrawerComponent) {
      const hostElement = rightDrawerComponent.location.nativeElement as HTMLElement;
      hostElement.classList.add('flex-1', 'flex', 'flex-col', 'min-h-0');
      host.insert(rightDrawerComponent.hostView);
    }
  })

  protected readonly bootstrapArrowLeft = bootstrapArrowLeft;
  protected readonly bootstrapList = bootstrapList;
  protected readonly featherChevronRight = featherChevronRight;
  protected readonly bootstrapQuestionCircle = bootstrapQuestionCircle;
}
