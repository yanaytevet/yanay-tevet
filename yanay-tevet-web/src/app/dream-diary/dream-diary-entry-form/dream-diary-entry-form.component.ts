import {Component, computed, inject, signal} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherArrowLeft} from '@ng-icons/feather-icons';
import {
  createDreamDiaryEntryView,
  getDreamDiaryEntryView,
  updateDreamDiaryEntryView,
} from '../../../generated-files/api/dream-diary';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-dream-diary-entry-form',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherArrowLeft})],
  templateUrl: './dream-diary-entry-form.component.html',
})
export class DreamDiaryEntryFormComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);

  readonly entryId = signal<number | null>(null);
  readonly isEditMode = computed(() => this.entryId() !== null);
  readonly isLoading = signal<boolean>(false);
  readonly isSaving = signal<boolean>(false);
  readonly loadError = signal<string | null>(null);

  readonly textCtrl = new FormControl<string>('');
  readonly timeCtrl = new FormControl<string>(this.getTodayLocalDatetimeString());

  private readonly textValue = toSignal(this.textCtrl.valueChanges, {initialValue: ''});
  readonly canSave = computed(
    () => !!this.textValue()?.trim() && !this.isSaving() && !this.isLoading(),
  );

  readonly featherArrowLeft = featherArrowLeft;

  constructor() {
    this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.entryId.set(id);
        void this.loadEntry(id);
      } else {
        this.entryId.set(null);
      }
    });
  }

  private getTodayLocalDatetimeString(): string {
    const now = new Date();
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
  }

  private toLocalDatetimeString(isoString: string): string {
    const d = new Date(isoString);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  private async loadEntry(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const res = await getDreamDiaryEntryView({path: {object_id: id}});
      this.textCtrl.setValue(res.data.text);
      this.timeCtrl.setValue(this.toLocalDatetimeString(res.data.time));
    } catch {
      this.loadError.set('Could not load this dream. It may have been deleted.');
    } finally {
      this.isLoading.set(false);
    }
  }

  async onSave(): Promise<void> {
    const text = this.textCtrl.value?.trim();
    if (!text || this.isSaving()) {
      return;
    }
    this.isSaving.set(true);
    try {
      const time = this.timeCtrl.value
        ? new Date(this.timeCtrl.value).toISOString()
        : new Date().toISOString();
      const id = this.entryId();
      if (id !== null) {
        await updateDreamDiaryEntryView({
          body: {text, time},
          path: {object_id: id},
        });
      } else {
        await createDreamDiaryEntryView({body: {text, time}});
      }
      await this.routingService.navigateToDreamDiary();
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to save dream: ${err}`,
      });
    } finally {
      this.isSaving.set(false);
    }
  }

  async onCancel(): Promise<void> {
    await this.routingService.navigateToDreamDiary();
  }
}
