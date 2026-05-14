import {inject, Injectable} from '@angular/core';
import {Cloudinary} from '@cloudinary/url-gen';
import {GlobalConfigurationsService} from './global-configurations.service';

@Injectable({
  providedIn: 'root'
})
export class CloudinaryService {
  private readonly configurationsService = inject(GlobalConfigurationsService);

  getImageUrl(publicId: string, width?: number, height?: number): string {
    const cloudName = this.configurationsService.cloudinaryCloudName();
    if (!cloudName || !publicId) {
      return '';
    }
    const cld = new Cloudinary({cloud: {cloudName}});
    const img = cld.image(publicId);
    if (width) {
      img.addTransformation(`w_${width}`);
    }
    if (height) {
      img.addTransformation(`h_${height}`);
    }
    return img.toURL();
  }
}
