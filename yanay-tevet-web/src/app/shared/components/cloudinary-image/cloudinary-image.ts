import {Component, computed, inject, input, output} from '@angular/core';
import {CloudinaryService} from '../../services/cloudinary.service';

@Component({
  selector: 'app-cloudinary-image',
  standalone: true,
  imports: [],
  templateUrl: './cloudinary-image.html',
})
export class CloudinaryImage {
  private readonly cloudinaryService = inject(CloudinaryService);

  readonly publicId = input.required<string>();
  readonly alt = input<string>('Image');
  readonly cssClass = input<string>('w-full h-full object-cover');
  readonly width = input<number | null>(null);
  readonly height = input<number | null>(null);

  readonly imageUrl = computed(() =>
    this.cloudinaryService.getImageUrl(this.publicId(), this.width(), this.height())
  );
}
