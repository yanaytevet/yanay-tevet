import {Component, ElementRef, inject, input, OnDestroy, OnInit, signal} from '@angular/core';
import {CloudinaryImage} from '../cloudinary-image/cloudinary-image';

@Component({
  selector: 'app-mobile-image-hero',
  standalone: true,
  imports: [CloudinaryImage],
  templateUrl: './mobile-image-hero.html',
})
export class MobileImageHero implements OnInit, OnDestroy {
  private readonly elementRef = inject(ElementRef);

  readonly publicId = input.required<string>();
  readonly alt = input<string>('');

  readonly scale = signal(1);
  readonly darkOverlayOpacity = signal(0);

  private scrollContainer: HTMLElement | null = null;
  private boundScrollHandler = this.onScroll.bind(this);

  ngOnInit() {
    this.scrollContainer = this.findScrollContainer();
    if (this.scrollContainer) {
      this.scrollContainer.addEventListener('scroll', this.boundScrollHandler, {passive: true});
    }
  }

  ngOnDestroy() {
    if (this.scrollContainer) {
      this.scrollContainer.removeEventListener('scroll', this.boundScrollHandler);
    }
  }

  private findScrollContainer(): HTMLElement | null {
    let el: HTMLElement | null = this.elementRef.nativeElement.parentElement;
    while (el) {
      const overflowY = window.getComputedStyle(el).overflowY;
      if (overflowY === 'auto' || overflowY === 'scroll') {
        return el;
      }
      el = el.parentElement;
    }
    return null;
  }

  private onScroll() {
    if (!this.scrollContainer) {
      return;
    }
    const scrollY = this.scrollContainer.scrollTop;
    const heroHeight = 220;
    const progress = Math.min(scrollY / heroHeight, 1);

    this.scale.set(1 - progress * 0.08);
    this.darkOverlayOpacity.set(progress * 0.55);
  }
}
