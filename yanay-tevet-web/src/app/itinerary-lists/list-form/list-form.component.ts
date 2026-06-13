import {Component, computed, inject, signal} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherArrowLeft} from '@ng-icons/feather-icons';
import {
  createItineraryListView,
  getItineraryListView,
  updateItineraryListView,
} from '../../../generated-files/api/itinerary-lists';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-itinerary-list-form',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherArrowLeft})],
  templateUrl: './list-form.component.html',
})
export class ListFormComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);

  readonly listId = signal<number | null>(null);
  readonly isEditMode = computed(() => this.listId() !== null);
  readonly isLoading = signal<boolean>(false);
  readonly isSaving = signal<boolean>(false);
  readonly loadError = signal<string | null>(null);

  readonly nameCtrl = new FormControl<string>('', {nonNullable: true});
  readonly descriptionCtrl = new FormControl<string>('', {nonNullable: true});

  private readonly nameValue = toSignal(this.nameCtrl.valueChanges, {initialValue: ''});
  readonly canSave = computed(() => !!this.nameValue()?.trim() && !this.isSaving() && !this.isLoading());

  protected readonly featherArrowLeft = featherArrowLeft;

  constructor() {
    this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.listId.set(id);
        void this.loadList(id);
      } else {
        this.listId.set(null);
      }
    });
  }

  private async loadList(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const res = await getItineraryListView({path: {object_id: id}});
      this.nameCtrl.setValue(res.data.name);
      this.descriptionCtrl.setValue(res.data.description);
    } catch {
      this.loadError.set('Could not load this list. You may not have access to it.');
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
      };
      const id = this.listId();
      if (id !== null) {
        await updateItineraryListView({body, path: {object_id: id}});
        await this.routingService.navigateToItineraryList(id);
      } else {
        const res = await createItineraryListView({body});
        await this.routingService.navigateToItineraryList(res.data.id);
      }
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to save list: ${err}`,
      });
    } finally {
      this.isSaving.set(false);
    }
  }

  async onCancel(): Promise<void> {
    const id = this.listId();
    if (id !== null) {
      await this.routingService.navigateToItineraryList(id);
    } else {
      await this.routingService.navigateToItineraryLists();
    }
  }
}
