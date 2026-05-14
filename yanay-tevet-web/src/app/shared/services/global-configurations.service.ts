import {computed, Injectable, signal} from '@angular/core';
import {FullConfigurationsOutput, fullConfigurationsView} from '../../../generated-files/api/configurations';

@Injectable({
  providedIn: 'root'
})
export class GlobalConfigurationsService {
  public fullConfigurations = signal<FullConfigurationsOutput>(null);

  readonly cloudinaryCloudName = computed(() => this.fullConfigurations()?.cloudinary_cloud_name ?? null);

  async loadConfigurations() {
    this.fullConfigurations.set((await fullConfigurationsView()).data);
  }
}
