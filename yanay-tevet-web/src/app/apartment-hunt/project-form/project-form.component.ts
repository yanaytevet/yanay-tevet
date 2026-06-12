import {Component, computed, inject, signal} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherArrowLeft} from '@ng-icons/feather-icons';
import {
  createRentalProjectView,
  Currency,
  getRentalProjectView,
  updateRentalProjectView,
} from '../../../generated-files/api/apartment-hunt';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';
import {CURRENCY_LABELS, CURRENCY_ORDER} from '../apartment-hunt.constants';

@Component({
  selector: 'app-apartment-hunt-project-form',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherArrowLeft})],
  templateUrl: './project-form.component.html',
})
export class ProjectFormComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);

  readonly projectId = signal<number | null>(null);
  readonly isEditMode = computed(() => this.projectId() !== null);
  readonly isLoading = signal<boolean>(false);
  readonly isSaving = signal<boolean>(false);
  readonly loadError = signal<string | null>(null);

  readonly nameCtrl = new FormControl<string>('', {nonNullable: true});
  readonly descriptionCtrl = new FormControl<string>('', {nonNullable: true});
  readonly currencyCtrl = new FormControl<Currency>('nis', {nonNullable: true});

  private readonly nameValue = toSignal(this.nameCtrl.valueChanges, {initialValue: ''});
  readonly canSave = computed(() => !!this.nameValue()?.trim() && !this.isSaving() && !this.isLoading());

  readonly currencyOptions = CURRENCY_ORDER;
  readonly currencyLabels = CURRENCY_LABELS;

  protected readonly featherArrowLeft = featherArrowLeft;

  constructor() {
    this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.projectId.set(id);
        void this.loadProject(id);
      } else {
        this.projectId.set(null);
      }
    });
  }

  private async loadProject(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const res = await getRentalProjectView({path: {object_id: id}});
      this.nameCtrl.setValue(res.data.name);
      this.descriptionCtrl.setValue(res.data.description);
      this.currencyCtrl.setValue(res.data.currency);
    } catch {
      this.loadError.set('Could not load this project. You may not have access to it.');
    } finally {
      this.isLoading.set(false);
    }
  }

  async onSave(): Promise<void> {
    const name = this.nameCtrl.value.trim();
    if (!name || this.isSaving()) {
      return;
    }
    this.isSaving.set(true);
    try {
      const body = {
        name,
        description: this.descriptionCtrl.value.trim(),
        currency: this.currencyCtrl.value,
      };
      const id = this.projectId();
      if (id !== null) {
        await updateRentalProjectView({body, path: {object_id: id}});
        await this.routingService.navigateToApartmentHuntProject(id);
      } else {
        const res = await createRentalProjectView({body});
        await this.routingService.navigateToApartmentHuntProject(res.data.id);
      }
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to save project: ${err}`,
      });
    } finally {
      this.isSaving.set(false);
    }
  }

  async onCancel(): Promise<void> {
    const id = this.projectId();
    if (id !== null) {
      await this.routingService.navigateToApartmentHuntProject(id);
    } else {
      await this.routingService.navigateToApartmentHunt();
    }
  }
}
