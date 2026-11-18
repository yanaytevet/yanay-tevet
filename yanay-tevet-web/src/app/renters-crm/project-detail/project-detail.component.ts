import {Component, computed, inject, signal} from '@angular/core';
import {ActivatedRoute, RouterLink} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {
  featherArrowLeft,
  featherChevronRight,
  featherCheckCircle,
  featherEdit,
  featherMoreHorizontal,
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
import {moneyFormat, RENTER_STATUS_ORDER} from '../renters-crm.constants';
import {fill, injectStrings, plural} from '../../shared/i18n/strings';
import {LanguageService} from '../../shared/i18n/language.service';
import {RENTERS_CRM_STRINGS} from '../i18n';
import {ShareDialogComponent} from '../../common/dialogs/share-dialog/share-dialog.component';
import {MenuButtonComponent, MenuItem, SEPARATOR} from '../../common/components/menu-button/menu-button.component';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {ErrorStateComponent} from '../../common/components/page/error-state/error-state.component';
import {RenterDetailsPanelComponent} from '../renter-details-panel/renter-details-panel.component';

@Component({
  selector: 'app-renters-project-detail',
  standalone: true,
  imports: [
    NgIcon, RenterDetailsPanelComponent, RouterLink, MenuButtonComponent,
    PageHeaderComponent, EmptyStateComponent, LoadingStateComponent, ErrorStateComponent,
  ],
  providers: [provideIcons({
    featherArrowLeft, featherChevronRight, featherCheckCircle, featherEdit, featherMoreHorizontal, featherPlus,
    featherRotateCcw, featherShare2, featherTrash2,
  })],
  templateUrl: './project-detail.component.html',
})
export class RentersProjectDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);

  readonly allProjectsUrl = this.routingService.getRentersCrmUrl();
  private readonly dialogService = inject(DialogService);
  private readonly authService = inject(AuthenticationService);
  private readonly languageService = inject(LanguageService);
  protected readonly t = injectStrings(RENTERS_CRM_STRINGS);

  readonly projectId = signal<number | null>(null);
  readonly project = signal<RentalProjectSchema | null>(null);
  readonly renters = signal<RenterProspectSchema[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly loadError = signal<boolean>(false);
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

  readonly headerSubtitle = computed(() => {
    const project = this.project();
    if (project === null) {
      return null;
    }
    const t = this.t();
    const language = this.languageService.language();
    const parts = [t.currencies[project.currency]];
    if (project.initial_asked_rent !== null) {
      parts.push(fill(t.common.askingRent, {amount: moneyFormat(language, project.currency).format(project.initial_asked_rent)}));
    }
    parts.push(fill(t.detail.owner, {name: project.owner_username}));
    parts.push(plural(language, project.member_count, t.common.members));
    return parts.join(' · ');
  });

  // Agreed rent and visit time per renter, in the site language's format.
  readonly rentLabels = computed<Record<number, string | null>>(() => {
    const project = this.project();
    if (project === null) {
      return {};
    }
    const money = moneyFormat(this.languageService.language(), project.currency);
    return Object.fromEntries(this.renters().map(r => [r.id, r.agreed_rent === null ? null : money.format(r.agreed_rent)]));
  });

  readonly visitLabels = computed<Record<number, string>>(() => {
    const format = new Intl.DateTimeFormat(this.languageService.language(), {dateStyle: 'short', timeStyle: 'short'});
    return Object.fromEntries(this.renters().map(r => [r.id, r.visit_time ? format.format(new Date(r.visit_time)) : '—']));
  });

  // Share and Edit sit in the header; finishing and deleting live behind "more".
  readonly overflowActions = computed<MenuItem[]>(() => {
    const t = this.t().detail;
    const actions: MenuItem[] = [
      {
        display: this.isFinished() ? t.reopen : t.finish,
        icon: this.isFinished() ? featherRotateCcw : featherCheckCircle,
        disabled: this.isUpdatingStatus(),
        callback: () => void this.toggleFinished(),
      },
    ];
    if (this.isOwner()) {
      actions.push(SEPARATOR);
      actions.push({display: t.deleteProject, icon: featherTrash2, danger: true, callback: () => void this.deleteProject()});
    }
    return actions;
  });

  readonly statusOptions = RENTER_STATUS_ORDER;

  protected readonly featherArrowLeft = featherArrowLeft;
  protected readonly featherChevronRight = featherChevronRight;
  protected readonly featherCheckCircle = featherCheckCircle;
  protected readonly featherEdit = featherEdit;
  protected readonly featherMoreHorizontal = featherMoreHorizontal;
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
    this.loadError.set(false);
    try {
      const [projectRes, rentersRes] = await Promise.all([
        getRentalProjectView({path: {object_id: id}}),
        paginateRenterProspectsView({path: {project_id: id}, query: {page: 0, page_size: 200}}),
      ]);
      this.project.set(projectRes.data);
      this.renters.set(rentersRes.data.data);
    } catch {
      this.loadError.set(true);
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
      await this.dialogService.showNotificationDialog({title: this.t().common.error, text: `${err}`});
    } finally {
      this.savingFieldId.set(null);
    }
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
    const t = this.t();
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: finished ? t.detail.reopenTitle : t.detail.finishTitle,
      text: finished ? t.detail.reopenText : t.detail.finishText,
      confirmActionName: finished ? t.detail.reopen : t.detail.finish,
      cancelActionName: t.common.cancel,
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
      await this.dialogService.showNotificationDialog({title: t.common.error, text: `${err}`});
    } finally {
      this.isUpdatingStatus.set(false);
    }
  }

  async openShareDialog(): Promise<void> {
    const id = this.projectId();
    if (id === null) {
      return;
    }
    const t = this.t().detail;
    await this.dialogService.open(ShareDialogComponent, {
      objectId: id,
      isOwner: this.isOwner(),
      title: t.shareTitle,
      subtitle: t.shareSubtitle,
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
    const t = this.t();
    const confirmed = await this.dialogService.getBooleanFromTextConfirmationDialog({
      title: t.detail.deleteProject,
      text: t.detail.deleteProjectText,
      label: t.detail.projectName,
      validationText: project.name,
      confirmActionName: t.detail.deleteProject,
      cancelActionName: t.common.cancel,
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteRentalProjectView({path: {object_id: project.id}});
      await this.routingService.navigateToRentersCrm();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: t.common.error, text: `${err}`});
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
    const t = this.t();
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: t.detail.deleteRenter,
      text: fill(t.detail.deleteRenterText, {name: renter.name || t.detail.thisRenter}),
      confirmActionName: t.common.delete,
      danger: true,
      cancelActionName: t.common.cancel,
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteRenterProspectView({path: {object_id: renter.id}});
      this.renters.update(prev => prev.filter(r => r.id !== renter.id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: t.common.error, text: `${err}`});
    }
  }
}
