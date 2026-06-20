import {Component, computed, inject, signal} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, FormGroup, ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherArrowLeft} from '@ng-icons/feather-icons';
import {
  createRenterProspectView,
  FamilyStatus,
  getRenterProspectView,
  RenterStatus,
  updateRenterProspectView,
} from '../../../generated-files/api/renters-crm';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';
import {
  FAMILY_STATUS_LABELS,
  FAMILY_STATUS_ORDER,
  RENTER_STATUS_LABELS,
  RENTER_STATUS_ORDER,
} from '../renters-crm.constants';

@Component({
  selector: 'app-renter-form',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherArrowLeft})],
  templateUrl: './renter-form.component.html',
})
export class RenterFormComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);

  readonly projectId = signal<number>(0);
  readonly renterId = signal<number | null>(null);
  readonly isEditMode = computed(() => this.renterId() !== null);
  readonly isLoading = signal<boolean>(false);
  readonly isSaving = signal<boolean>(false);
  readonly loadError = signal<string | null>(null);

  readonly form = new FormGroup({
    name: new FormControl<string>('', {nonNullable: true}),
    status: new FormControl<RenterStatus>('contacted', {nonNullable: true}),
    family_status: new FormControl<FamilyStatus>('single', {nonNullable: true}),
    visit_time: new FormControl<string>('', {nonNullable: true}),
    saw_apartment: new FormControl<boolean>(false, {nonNullable: true}),
    has_animals: new FormControl<boolean>(false, {nonNullable: true}),
    long_term: new FormControl<boolean>(false, {nonNullable: true}),
    agreed_rent: new FormControl<number | null>(null),
    notes: new FormControl<string>('', {nonNullable: true}),
  });

  private readonly nameValue = toSignal(this.form.controls.name.valueChanges, {initialValue: ''});
  readonly canSave = computed(() => !!this.nameValue()?.trim() && !this.isSaving() && !this.isLoading());

  readonly statusOptions = RENTER_STATUS_ORDER;
  readonly statusLabels = RENTER_STATUS_LABELS;
  readonly familyStatusOptions = FAMILY_STATUS_ORDER;
  readonly familyStatusLabels = FAMILY_STATUS_LABELS;

  protected readonly featherArrowLeft = featherArrowLeft;

  constructor() {
    this.route.paramMap.subscribe(params => {
      this.projectId.set(Number(params.get('projectId')));
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.renterId.set(id);
        void this.loadRenter(id);
      } else {
        this.renterId.set(null);
      }
    });
  }

  private async loadRenter(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const res = await getRenterProspectView({path: {object_id: id}});
      const r = res.data;
      this.form.patchValue({
        name: r.name,
        status: r.status,
        family_status: r.family_status,
        visit_time: this.toLocalInput(r.visit_time),
        saw_apartment: r.saw_apartment,
        has_animals: r.has_animals,
        long_term: r.long_term,
        agreed_rent: r.agreed_rent,
        notes: r.notes,
      });
    } catch {
      this.loadError.set('Could not load this renter. It may have been deleted.');
    } finally {
      this.isLoading.set(false);
    }
  }

  private toLocalInput(iso: string | null): string {
    if (!iso) {
      return '';
    }
    const d = new Date(iso);
    const pad = (n: number) => `${n}`.padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  private fromLocalInput(local: string): string | null {
    if (!local) {
      return null;
    }
    return new Date(local).toISOString();
  }

  async onSave(): Promise<void> {
    if (!this.canSave()) {
      return;
    }
    this.isSaving.set(true);
    try {
      const raw = this.form.getRawValue();
      const body = {
        name: raw.name.trim(),
        status: raw.status,
        family_status: raw.family_status,
        visit_time: this.fromLocalInput(raw.visit_time),
        saw_apartment: raw.saw_apartment,
        has_animals: raw.has_animals,
        long_term: raw.long_term,
        agreed_rent: raw.agreed_rent,
        notes: raw.notes,
      };
      const id = this.renterId();
      if (id !== null) {
        await updateRenterProspectView({body, path: {object_id: id}});
      } else {
        await createRenterProspectView({body: {...body, project_id: this.projectId()}});
      }
      await this.routingService.navigateToRentersCrmProject(this.projectId());
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `Failed to save renter: ${err}`});
    } finally {
      this.isSaving.set(false);
    }
  }

  async onCancel(): Promise<void> {
    await this.routingService.navigateToRentersCrmProject(this.projectId());
  }
}
