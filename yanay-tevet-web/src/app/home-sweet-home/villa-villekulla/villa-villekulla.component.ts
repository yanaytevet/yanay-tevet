import {Component, computed, inject, signal} from '@angular/core';
import {Router, RouterLink} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherPlus, featherChevronRight} from '@ng-icons/feather-icons';
import {
  createVillaVillekullaProjectView,
  paginateVillaVillekullaProjectsView,
  RentalProjectSchema,
} from '../../../generated-files/api/villa-villekulla';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {injectStrings} from '../../shared/i18n/strings';
import {HOME_SWEET_HOME_STRINGS} from '../i18n';

@Component({
  selector: 'app-villa-villekulla',
  standalone: true,
  imports: [NgIcon, RouterLink, PageHeaderComponent, EmptyStateComponent, LoadingStateComponent],
  providers: [provideIcons({featherPlus, featherChevronRight})],
  templateUrl: './villa-villekulla.component.html',
})
export class VillaVillekullaComponent {
  private readonly authService = inject(AuthenticationService);
  private readonly dialogService = inject(DialogService);
  private readonly routingService = inject(RoutingService);
  private readonly router = inject(Router);
  protected readonly t = injectStrings(HOME_SWEET_HOME_STRINGS);

  readonly isLoading = signal<boolean>(true);
  readonly projects = signal<RentalProjectSchema[]>([]);

  readonly isSiteAdmin = computed<boolean>(() => this.authService.user()?.is_admin ?? false);

  readonly projectUrls = computed(() =>
    Object.fromEntries(this.projects().map(p => [p.id, this.routingService.getVillaVillekullaProjectUrl(p.id)]))
  );

  protected readonly featherPlus = featherPlus;
  protected readonly featherChevronRight = featherChevronRight;

  constructor() {
    void this.load();
  }

  private async load(): Promise<void> {
    this.isLoading.set(true);
    try {
      const res = await paginateVillaVillekullaProjectsView({query: {page: 0, page_size: 50}});
      const projects = res.data.data;
      this.projects.set(projects);
      if (projects.length === 1 && !this.isSiteAdmin()) {
        await this.router.navigateByUrl(this.routingService.getVillaVillekullaProjectUrl(projects[0].id), {replaceUrl: true});
        return;
      }
    } finally {
      this.isLoading.set(false);
    }
  }

  async createProject(): Promise<void> {
    const t = this.t();
    const name = await this.dialogService.getTextFromInputDialog({
      title: t.list.createTitle,
      text: t.list.createText,
      label: t.list.propertyName,
      defaultValue: t.list.defaultName,
      confirmActionName: t.list.create,
      cancelActionName: t.common.cancel,
    });
    if (!name) {
      return;
    }
    try {
      const res = await createVillaVillekullaProjectView({body: {name}});
      await this.routingService.navigateToVillaVillekullaProject(res.data.id);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: t.common.error, text: `${err}`});
    }
  }
}
