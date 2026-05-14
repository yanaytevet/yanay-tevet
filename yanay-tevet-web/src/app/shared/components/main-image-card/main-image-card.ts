import {Component, input, output} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {bootstrapEye, bootstrapEyeSlash, bootstrapStarFill} from '@ng-icons/bootstrap-icons';
import {heroCamera} from '@ng-icons/heroicons/outline';
import {CloudinaryImage} from '../cloudinary-image/cloudinary-image';
import {MobileImageHero} from '../mobile-image-hero/mobile-image-hero';
import {ImageOutput} from '../../../../generated-files/api/images';

@Component({
  selector: 'app-main-image-card',
  standalone: true,
  imports: [NgIcon, CloudinaryImage, MobileImageHero],
  providers: [provideIcons({heroCamera, bootstrapStarFill, bootstrapEye, bootstrapEyeSlash})],
  templateUrl: './main-image-card.html',
})
export class MainImageCard {
  readonly mainImage = input<ImageOutput | null>(null);
  readonly entityName = input<string>('');
  readonly isEditing = input<boolean>(false);
  readonly isUploading = input<boolean>(false);
  readonly showVisibility = input<boolean>(false);

  readonly uploadImage = output<File>();
  readonly toggleMain = output<number>();
  readonly toggleVisibility = output<number>();

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      this.uploadImage.emit(input.files[0]);
      input.value = '';
    }
  }

  protected readonly heroCamera = heroCamera;
  protected readonly bootstrapStarFill = bootstrapStarFill;
  protected readonly bootstrapEye = bootstrapEye;
  protected readonly bootstrapEyeSlash = bootstrapEyeSlash;
}
