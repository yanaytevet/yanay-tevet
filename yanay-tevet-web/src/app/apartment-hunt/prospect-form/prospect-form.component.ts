import {Component, computed, inject, signal} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, FormGroup, ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherArrowLeft, featherPlus, featherTrash2, featherUpload, featherX} from '@ng-icons/feather-icons';
import {
  ApartmentImageSchema,
  ApartmentProspectSchema,
  ContactMethod,
  createApartmentProspectView,
  deleteApartmentImageView,
  getApartmentProspectView,
  ProspectStatus,
  updateApartmentProspectView,
  uploadApartmentProspectImageView,
} from '../../../generated-files/api/apartment-hunt';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {FilesUploadService} from '../../common/services/files-upload.service';
import {RoutingService} from '../../shared/services/routing.service';
import {
  CONTACT_METHOD_LABELS,
  CONTACT_METHOD_ORDER,
  PROSPECT_STATUS_LABELS,
  PROSPECT_STATUS_ORDER,
} from '../apartment-hunt.constants';

type ContactGroup = FormGroup<{
  method: FormControl<ContactMethod>;
  value: FormControl<string>;
  label: FormControl<string>;
}>;

@Component({
  selector: 'app-apartment-hunt-prospect-form',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherArrowLeft, featherPlus, featherTrash2, featherUpload, featherX})],
  templateUrl: './prospect-form.component.html',
})
export class ProspectFormComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);
  private readonly filesUploadService = inject(FilesUploadService);

  readonly projectId = signal<number>(0);
  readonly prospectId = signal<number | null>(null);
  readonly isEditMode = computed(() => this.prospectId() !== null);
  readonly isLoading = signal<boolean>(false);
  readonly isSaving = signal<boolean>(false);
  readonly isUploading = signal<boolean>(false);
  readonly loadError = signal<string | null>(null);
  readonly images = signal<ApartmentImageSchema[]>([]);

  readonly form = new FormGroup({
    title: new FormControl<string>('', {nonNullable: true}),
    status: new FormControl<ProspectStatus>('saw', {nonNullable: true}),
    town: new FormControl<string>('', {nonNullable: true}),
    full_address: new FormControl<string>('', {nonNullable: true}),
    monthly_rent: new FormControl<number | null>(null),
    via_agency: new FormControl<boolean>(false, {nonNullable: true}),
    agency_fee: new FormControl<number | null>(null),
    monthly_tax_benefit: new FormControl<number | null>(null),
    has_protected_room: new FormControl<boolean>(false, {nonNullable: true}),
    liked_level: new FormControl<number | null>(null),
    rooms: new FormControl<number | null>(null),
    floor: new FormControl<number | null>(null),
    size_sqm: new FormControl<number | null>(null),
    available_from: new FormControl<string | null>(null),
    listing_url: new FormControl<string>('', {nonNullable: true}),
    notes: new FormControl<string>('', {nonNullable: true}),
  });

  readonly contacts = signal<ContactGroup[]>([]);

  private readonly formValue = toSignal(this.form.valueChanges, {initialValue: this.form.getRawValue()});
  readonly canSave = computed(() => {
    const value = this.formValue();
    const hasIdentity = !!value.title?.trim() || !!value.full_address?.trim();
    return hasIdentity && !this.isSaving() && !this.isLoading();
  });

  readonly statusOptions = PROSPECT_STATUS_ORDER;
  readonly statusLabels = PROSPECT_STATUS_LABELS;
  readonly contactMethodOptions = CONTACT_METHOD_ORDER;
  readonly contactMethodLabels = CONTACT_METHOD_LABELS;
  readonly likedLevels = [1, 2, 3, 4, 5];

  protected readonly featherArrowLeft = featherArrowLeft;
  protected readonly featherPlus = featherPlus;
  protected readonly featherTrash2 = featherTrash2;
  protected readonly featherUpload = featherUpload;
  protected readonly featherX = featherX;

  constructor() {
    this.route.paramMap.subscribe(params => {
      this.projectId.set(Number(params.get('projectId')));
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.prospectId.set(id);
        void this.loadProspect(id);
      } else {
        this.prospectId.set(null);
        this.contacts.set([this.buildContactGroup()]);
      }
    });
  }

  private buildContactGroup(method: ContactMethod = 'whatsapp', value = '', label = ''): ContactGroup {
    return new FormGroup({
      method: new FormControl<ContactMethod>(method, {nonNullable: true}),
      value: new FormControl<string>(value, {nonNullable: true}),
      label: new FormControl<string>(label, {nonNullable: true}),
    });
  }

  private async loadProspect(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const res = await getApartmentProspectView({path: {object_id: id}});
      const p = res.data;
      this.form.patchValue({
        title: p.title,
        status: p.status,
        town: p.town,
        full_address: p.full_address,
        monthly_rent: p.monthly_rent,
        via_agency: p.via_agency,
        agency_fee: p.agency_fee,
        monthly_tax_benefit: p.monthly_tax_benefit,
        has_protected_room: p.has_protected_room,
        liked_level: p.liked_level,
        rooms: p.rooms,
        floor: p.floor,
        size_sqm: p.size_sqm,
        available_from: p.available_from,
        listing_url: p.listing_url,
        notes: p.notes,
      });
      this.contacts.set(p.contacts.map(c => this.buildContactGroup(c.method, c.value, c.label)));
      this.images.set(p.images);
    } catch {
      this.loadError.set('Could not load this apartment. It may have been deleted.');
    } finally {
      this.isLoading.set(false);
    }
  }

  addContact(): void {
    this.contacts.update(prev => [...prev, this.buildContactGroup()]);
  }

  removeContact(group: ContactGroup): void {
    this.contacts.update(prev => prev.filter(g => g !== group));
  }

  private collectContacts() {
    return this.contacts()
      .map(g => g.getRawValue())
      .filter(c => c.value.trim() !== '');
  }

  async onSave(): Promise<void> {
    if (!this.canSave()) {
      return;
    }
    this.isSaving.set(true);
    try {
      const raw = this.form.getRawValue();
      const writable = {
        ...raw,
        available_from: raw.available_from || null,
      };
      const contacts = this.collectContacts();
      const id = this.prospectId();
      if (id !== null) {
        await updateApartmentProspectView({body: {...writable, contacts}, path: {object_id: id}});
      } else {
        await createApartmentProspectView({body: {...writable, project_id: this.projectId(), contacts}});
      }
      await this.routingService.navigateToApartmentHuntProject(this.projectId());
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `Failed to save apartment: ${err}`});
    } finally {
      this.isSaving.set(false);
    }
  }

  async onCancel(): Promise<void> {
    await this.routingService.navigateToApartmentHuntProject(this.projectId());
  }

  async uploadImage(): Promise<void> {
    const id = this.prospectId();
    if (id === null) {
      return;
    }
    try {
      const updated = await this.filesUploadService.uploadFile<ApartmentProspectSchema>(
        'image/*',
        async (files: File[]) => {
          this.isUploading.set(true);
          const res = await uploadApartmentProspectImageView({body: {files}, path: {object_id: id}});
          return res.data;
        },
      );
      this.images.set(updated.images);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `Failed to upload image: ${err}`});
    } finally {
      this.isUploading.set(false);
    }
  }

  async deleteImage(image: ApartmentImageSchema): Promise<void> {
    try {
      await deleteApartmentImageView({path: {object_id: image.id}});
      this.images.update(prev => prev.filter(i => i.id !== image.id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `Failed to delete image: ${err}`});
    }
  }
}
