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
  deleteRenterProspectView,
  deleteRentalProjectView,
  finishRentalProjectView,
  getRentalProjectView,
  listProjectMembersView,
  paginateRenterProspectsView,
  RenterProspectSchema,
  RenterStatus,
  RentalProjectSchema,
  reopenRentalProjectView,
  shareRentalProjectView,
  unshareRentalProjectView,
  updateRenterProspectView,
} from '../../../generated-files/api/renters-crm';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';
import {
  CURRENCY_SYMBOLS,
  FAMILY_STATUS_LABELS,
  PROJECT_STATUS_LABELS,
  RENTER_STATUS_LABELS,
  RENTER_STATUS_ORDER,
} from '../renters-crm.constants';
import {ShareDialogComponent} from '../../common/dialogs/share-dialog/share-dialog.component';
import {RenterDetailsPanelComponent} from '../renter-details-panel/renter-details-panel.component';

@Component({
  selector: 'app-renters-project-detail',
  standalone: true,
  imports: [NgIcon, DatePipe, RenterDetailsPanelComponent],
  providers: [provideIcons({
    featherArrowLeft, featherChevronRight, featherCheckCircle, featherEdit, featherPlus,
    featherRotateCcw, featherShare2, featherTrash2,
  })],
  templateUrl: './project-detail.component.html',
})
export class RentersProjectDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);
  private readonly authService = inject(AuthenticationService);

  readonly projectId = signal<number | null>(null);
  readonly project = signal<RentalProjectSchema | null>(null);
  readonly renters = signal<RenterProspectSchema[]>([]);
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
    return Object.fromEntries(this.renters().map(r => [r.id, ids.has(r.id)]));
  });

  readonly currencySymbols = CURRENCY_SYMBOLS;
  readonly projectStatusLabels = PROJECT_STATUS_LABELS;
  readonly renterStatusLabels = RENTER_STATUS_LABELS;
  readonly statusOptions = RENTER_STATUS_ORDER;
  readonly familyStatusLabels = FAMILY_STATUS_LABELS;

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
      const [projectRes, rentersRes] = await Promise.all([
        getRentalProjectView({path: {object_id: id}}),
        paginateRenterProspectsView({path: {project_id: id}, query: {page: 0, page_size: 200}}),
      ]);
      this.project.set(projectRes.data);
      this.renters.set(rentersRes.data.data);
    } catch {
      this.loadError.set('Could not load this project. You may not have access to it.');
    } finally {
      this.isLoading.set(false);
    }
  }

  toggleExpand(renter: RenterProspectSchema): void {
    this.expandedIds.update(prev => {
      const next = new Set(prev);
      if (next.has(renter.id)) {
        next.delete(renter.id);
      } else {
        next.add(renter.id);
      }
      return next;
    });
  }

  async onStatusChange(renter: RenterProspectSchema, value: string): Promise<void> {
    this.savingFieldId.set(renter.id);
    try {
      const res = await updateRenterProspectView({body: {status: value as RenterStatus}, path: {object_id: renter.id}});
      this.renters.update(prev => prev.map(r => (r.id === renter.id ? res.data : r)));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.savingFieldId.set(null);
    }
  }

  async back(): Promise<void> {
    await this.routingService.navigateToRentersCrm();
  }

  async editProject(): Promise<void> {
    const id = this.projectId();
    if (id !== null) {
      await this.routingService.navigateToRentersCrmEditProject(id);
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
    await this.dialogService.open(ShareDialogComponent, {
      objectId: id,
      isOwner: this.isOwner(),
      title: 'Share project',
      subtitle: 'People you add can view and edit this project\'s renters.',
      listMembers: async (objectId: number) => {
        const data = (await listProjectMembersView({path: {object_id: objectId}})).data;
        return {members: data.members, pendingInvitations: data.pending_invitations};
      },
      share: async (objectId: number, identifier: string) => {
        await shareRentalProjectView({body: {identifier, role: 'collaborator'}, path: {object_id: objectId}});
      },
      unshare: async (objectId: number, identifier: string) => {
        await unshareRentalProjectView({body: {identifier}, path: {object_id: objectId}});
      },
    }, 45);
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
      text: 'This permanently deletes the project and all of its renters. This cannot be undone.',
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
      await this.routingService.navigateToRentersCrm();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async addRenter(): Promise<void> {
    const id = this.projectId();
    if (id !== null) {
      await this.routingService.navigateToRentersCrmNewRenter(id);
    }
  }

  async editRenter(renter: RenterProspectSchema): Promise<void> {
    const id = this.projectId();
    if (id !== null) {
      await this.routingService.navigateToRentersCrmEditRenter(id, renter.id);
    }
  }

  async deleteRenter(renter: RenterProspectSchema): Promise<void> {
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'Delete renter',
      text: `Delete "${renter.name || 'this renter'}"?`,
      confirmActionName: 'Delete',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteRenterProspectView({path: {object_id: renter.id}});
      this.renters.update(prev => prev.filter(r => r.id !== renter.id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }
}
