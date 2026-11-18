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
  ApartmentProspectSchema,
  deleteApartmentProspectView,
  deleteRentalProjectView,
  finishRentalProjectView,
  getRentalProjectView,
  listProjectMembersView,
  paginateApartmentProspectsView,
  ProspectStatus,
  RentalProjectSchema,
  reopenRentalProjectView,
  shareRentalProjectView,
  unshareRentalProjectView,
  updateApartmentProspectView,
} from '../../../generated-files/api/apartment-hunt';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';
import {LIKED_OPTIONS, moneyFormat, parseDate, PROSPECT_STATUS_ORDER} from '../apartment-hunt.constants';
import {fill, injectStrings, plural} from '../../shared/i18n/strings';
import {LanguageService} from '../../shared/i18n/language.service';
import {APARTMENT_HUNT_STRINGS} from '../i18n';
import {ShareDialogComponent} from '../../common/dialogs/share-dialog/share-dialog.component';
import {MenuButtonComponent, MenuItem, SEPARATOR} from '../../common/components/menu-button/menu-button.component';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {ErrorStateComponent} from '../../common/components/page/error-state/error-state.component';
import {ProspectDetailsPanelComponent} from '../prospect-details-panel/prospect-details-panel.component';

@Component({
  selector: 'app-apartment-hunt-project-detail',
  standalone: true,
  imports: [
    NgIcon, ProspectDetailsPanelComponent, RouterLink, MenuButtonComponent,
    PageHeaderComponent, EmptyStateComponent, LoadingStateComponent, ErrorStateComponent,
  ],
  providers: [provideIcons({
    featherArrowLeft, featherChevronRight, featherCheckCircle, featherEdit, featherMoreHorizontal, featherPlus,
    featherRotateCcw, featherShare2, featherTrash2,
  })],
  templateUrl: './project-detail.component.html',
})
export class ProjectDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);

  readonly allProjectsUrl = this.routingService.getApartmentHuntUrl();
  private readonly dialogService = inject(DialogService);
  private readonly authService = inject(AuthenticationService);
  private readonly languageService = inject(LanguageService);
  protected readonly t = injectStrings(APARTMENT_HUNT_STRINGS);

  readonly projectId = signal<number | null>(null);
  readonly project = signal<RentalProjectSchema | null>(null);
  readonly prospects = signal<ApartmentProspectSchema[]>([]);
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
    return Object.fromEntries(this.prospects().map(p => [p.id, ids.has(p.id)]));
  });

  readonly headerSubtitle = computed(() => {
    const project = this.project();
    if (project === null) {
      return null;
    }
    const t = this.t();
    return [
      t.currencies[project.currency],
      fill(t.detail.owner, {name: project.owner_username}),
      plural(this.languageService.language(), project.member_count, t.common.members),
    ].join(' · ');
  });

  // Rent and last-update date per apartment, in the site language's format.
  readonly rentLabels = computed<Record<number, string | null>>(() => {
    const project = this.project();
    if (project === null) {
      return {};
    }
    const money = moneyFormat(this.languageService.language(), project.currency);
    return Object.fromEntries(this.prospects().map(p => [p.id, p.monthly_rent === null ? null : money.format(p.monthly_rent)]));
  });

  readonly updatedLabels = computed<Record<number, string>>(() => {
    const format = new Intl.DateTimeFormat(this.languageService.language(), {dateStyle: 'medium'});
    return Object.fromEntries(this.prospects().map(p => [p.id, format.format(parseDate(p.updated_at))]));
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

  readonly statusOptions = PROSPECT_STATUS_ORDER;
  readonly likedOptions = LIKED_OPTIONS;

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
      const [projectRes, prospectsRes] = await Promise.all([
        getRentalProjectView({path: {object_id: id}}),
        paginateApartmentProspectsView({path: {project_id: id}, query: {page: 0, page_size: 200}}),
      ]);
      this.project.set(projectRes.data);
      this.prospects.set(prospectsRes.data.data);
    } catch {
      this.loadError.set(true);
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
      await this.dialogService.showNotificationDialog({title: this.t().common.error, text: `${err}`});
    } finally {
      this.savingFieldId.set(null);
    }
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
      await this.routingService.navigateToApartmentHunt();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: t.common.error, text: `${err}`});
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
    const t = this.t();
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: t.detail.deleteApartment,
      text: fill(t.detail.deleteApartmentText, {name: prospect.title || prospect.full_address || t.detail.thisApartment}),
      confirmActionName: t.common.delete,
      danger: true,
      cancelActionName: t.common.cancel,
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteApartmentProspectView({path: {object_id: prospect.id}});
      this.prospects.update(prev => prev.filter(p => p.id !== prospect.id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: t.common.error, text: `${err}`});
    }
  }
}
