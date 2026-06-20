import {Component, computed, inject, signal} from '@angular/core';
import {Router} from '@angular/router';
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

@Component({
  selector: 'app-villa-villekulla',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({featherPlus, featherChevronRight})],
  templateUrl: './villa-villekulla.component.html',
})
export class VillaVillekullaComponent {
  private readonly authService = inject(AuthenticationService);
  private readonly dialogService = inject(DialogService);
  private readonly routingService = inject(RoutingService);
  private readonly router = inject(Router);

  readonly isLoading = signal<boolean>(true);
  readonly projects = signal<RentalProjectSchema[]>([]);

  readonly isSiteAdmin = computed<boolean>(() => this.authService.user()?.is_admin ?? false);

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

  async open(project: RentalProjectSchema): Promise<void> {
    await this.routingService.navigateToVillaVillekullaProject(project.id);
  }

  async createProject(): Promise<void> {
    const name = await this.dialogService.getTextFromInputDialog({
      title: 'Create property',
      text: 'Name this property. You can invite friends to book its unit once it exists.',
      label: 'Property name',
      defaultValue: 'Villa Villekulla',
      confirmActionName: 'Create',
    });
    if (!name) {
      return;
    }
    try {
      const res = await createVillaVillekullaProjectView({body: {name}});
      await this.routingService.navigateToVillaVillekullaProject(res.data.id);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }
}
