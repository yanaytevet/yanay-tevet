import {Component, computed, inject, signal} from '@angular/core';
import {DatePipe} from '@angular/common';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {
  featherArrowLeft,
  featherChevronRight,
  featherCheckCircle,
  featherEdit,
  featherPlus,
  featherRotateCcw,
  featherShare2,
  featherTrash2,
} from '@ng-icons/feather-icons';
import {
  ApartmentProspectSchema,
  deleteApartmentProspectView,
  deleteRentalProjectView,
  finishRentalProjectView,
  getRentalProjectView,
  paginateApartmentProspectsView,
  ProspectStatus,
  RentalProjectSchema,
  reopenRentalProjectView,
  updateApartmentProspectView,
} from '../../../generated-files/api/apartment-hunt';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';
import {
  CURRENCY_SYMBOLS,
  LIKED_OPTIONS,
  PROJECT_STATUS_LABELS,
  PROSPECT_STATUS_LABELS,
  PROSPECT_STATUS_ORDER,
} from '../apartment-hunt.constants';
import {ShareProjectDialogComponent} from '../dialogs/share-project-dialog/share-project-dialog.component';
import {ProspectDetailsPanelComponent} from '../prospect-details-panel/prospect-details-panel.component';

@Component({
  selector: 'app-apartment-hunt-project-detail',
  standalone: true,
  imports: [NgIcon, DatePipe, ProspectDetailsPanelComponent],
  providers: [provideIcons({
    featherArrowLeft, featherChevronRight, featherCheckCircle, featherEdit, featherPlus,
    featherRotateCcw, featherShare2, featherTrash2,
  })],
  templateUrl: './project-detail.component.html',
})
export class ProjectDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);
  private readonly authService = inject(AuthenticationService);

  readonly projectId = signal<number | null>(null);
  readonly project = signal<RentalProjectSchema | null>(null);
  readonly prospects = signal<ApartmentProspectSchema[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly loadError = signal<string | null>(null);
  readonly isUpdatingStatus = signal<boolean>(false);
  readonly expandedIds = signal<Set<number>>(new Set());
  readonly savingFieldId = signal<number | null>(null);

  readonly isOwner = computed(() => {
    const project = this.project();
    return !!project && project.owner_id === this.authService.user()?.id;
  });
  readonly isFinished = computed(() => this.project()?.status === 'finished');

  readonly expandedMap = computed(() => {
    const ids = this.expandedIds();
    return Object.fromEntries(this.prospects().map(p => [p.id, ids.has(p.id)]));
  });

  readonly currencySymbols = CURRENCY_SYMBOLS;
  readonly projectStatusLabels = PROJECT_STATUS_LABELS;
  readonly prospectStatusLabels = PROSPECT_STATUS_LABELS;
  readonly statusOptions = PROSPECT_STATUS_ORDER;
  readonly likedOptions = LIKED_OPTIONS;

  protected readonly featherArrowLeft = featherArrowLeft;
  protected readonly featherChevronRight = featherChevronRight;
  protected readonly featherCheckCircle = featherCheckCircle;
  protected readonly featherEdit = featherEdit;
  protected readonly featherPlus = featherPlus;
  protected readonly featherRotateCcw = featherRotateCcw;
  protected readonly featherShare2 = featherShare2;
  protected readonly featherTrash2 = featherTrash2;

  constructor() {
    this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.projectId.set(id);
        void this.load(id);
      }
    });
  }

  private async load(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const [projectRes, prospectsRes] = await Promise.all([
        getRentalProjectView({path: {object_id: id}}),
        paginateApartmentProspectsView({path: {project_id: id}, query: {page: 0, page_size: 200}}),
      ]);
      this.project.set(projectRes.data);
      this.prospects.set(prospectsRes.data.data);
    } catch {
      this.loadError.set('Could not load this project. You may not have access to it.');
    } finally {
      this.isLoading.set(false);
    }
  }

  toggleExpand(prospect: ApartmentProspectSchema): void {
    this.expandedIds.update(prev => {
      const next = new Set(prev);
      if (next.has(prospect.id)) {
        next.delete(prospect.id);
      } else {
        next.add(prospect.id);
      }
      return next;
    });
  }

  async onStatusChange(prospect: ApartmentProspectSchema, value: string): Promise<void> {
    await this.patchProspect(prospect, {status: value as ProspectStatus});
  }

  async onLikedChange(prospect: ApartmentProspectSchema, value: string): Promise<void> {
    await this.patchProspect(prospect, {liked_level: value === '' ? null : Number(value)});
  }

  private async patchProspect(
    prospect: ApartmentProspectSchema,
    body: {status?: ProspectStatus; liked_level?: number | null},
  ): Promise<void> {
    this.savingFieldId.set(prospect.id);
    try {
      const res = await updateApartmentProspectView({body, path: {object_id: prospect.id}});
      this.prospects.update(prev => prev.map(p => (p.id === prospect.id ? res.data : p)));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.savingFieldId.set(null);
    }
  }

  async back(): Promise<void> {
    await this.routingService.navigateToApartmentHunt();
  }

  async editProject(): Promise<void> {
    const id = this.projectId();
    if (id !== null) {
      await this.routingService.navigateToApartmentHuntEditProject(id);
    }
  }

  async toggleFinished(): Promise<void> {
    const id = this.projectId();
    if (id === null || this.isUpdatingStatus()) {
      return;
    }
    const finished = this.isFinished();
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: finished ? 'Reopen project' : 'Finish project',
      text: finished
        ? 'Reopen this project and mark it active again?'
        : 'Mark this project as finished? You can reopen it later.',
      confirmActionName: finished ? 'Reopen' : 'Finish',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    this.isUpdatingStatus.set(true);
    try {
      const res = finished
        ? await reopenRentalProjectView({body: {}, path: {object_id: id}})
        : await finishRentalProjectView({body: {}, path: {object_id: id}});
      this.project.set(res.data);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.isUpdatingStatus.set(false);
    }
  }

  async openShareDialog(): Promise<void> {
    const id = this.projectId();
    if (id === null) {
      return;
    }
    await this.dialogService.open(ShareProjectDialogComponent, {projectId: id, isOwner: this.isOwner()}, 45);
    const res = await getRentalProjectView({path: {object_id: id}});
    this.project.set(res.data);
  }

  async deleteProject(): Promise<void> {
    const project = this.project();
    if (project === null) {
      return;
    }
    const confirmed = await this.dialogService.getBooleanFromTextConfirmationDialog({
      title: 'Delete project',
      text: 'This permanently deletes the project and all of its apartments. This cannot be undone.',
      label: 'Project name',
      validationText: project.name,
      confirmActionName: 'Delete project',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteRentalProjectView({path: {object_id: project.id}});
      await this.routingService.navigateToApartmentHunt();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async addProspect(): Promise<void> {
    const id = this.projectId();
    if (id !== null) {
      await this.routingService.navigateToApartmentHuntNewProspect(id);
    }
  }

  async editProspect(prospect: ApartmentProspectSchema): Promise<void> {
    const id = this.projectId();
    if (id !== null) {
      await this.routingService.navigateToApartmentHuntEditProspect(id, prospect.id);
    }
  }

  async deleteProspect(prospect: ApartmentProspectSchema): Promise<void> {
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'Delete apartment',
      text: `Delete "${prospect.title || prospect.full_address || 'this apartment'}"?`,
      confirmActionName: 'Delete',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteApartmentProspectView({path: {object_id: prospect.id}});
      this.prospects.update(prev => prev.filter(p => p.id !== prospect.id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }
}
