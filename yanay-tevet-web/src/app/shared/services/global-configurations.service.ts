import {computed, Injectable, signal} from '@angular/core';
import {FullConfigurationsOutput, fullConfigurationsView} from '../../../generated-files/api/configurations';

@Injectable({
  providedIn: 'root'
})
export class GlobalConfigurationsService {
  public fullConfigurations = signal<FullConfigurationsOutput>(null);
  private loadingPromise: Promise<void> | null = null;

  readonly cloudinaryCloudName = computed(() => this.fullConfigurations()?.cloudinary_cloud_name ?? null);
  readonly googleClientId = computed(() => this.fullConfigurations()?.google_client_id ?? null);

  async loadConfigurations() {
    this.loadingPromise = fullConfigurationsView().then(res => {
      this.fullConfigurations.set(res.data);
    });
    await this.loadingPromise;
  }

  async waitForConfigurations(): Promise<void> {
    if (this.loadingPromise) {
      await this.loadingPromise;
    }
  }
}
