import {
  Directive,
  ElementRef,
  NgZone,
  OnDestroy,
  afterNextRender,
  inject,
  signal,
} from '@angular/core';

@Directive({
  selector: '[appDetectClamp]',
  standalone: true,
  exportAs: 'detectClamp',
})
export class DetectClampDirective implements OnDestroy {
  private readonly elRef = inject(ElementRef<HTMLElement>);
  private readonly zone = inject(NgZone);

  private ro?: ResizeObserver;

  readonly isClamped = signal(false);

  constructor() {
    afterNextRender(() => {
      const el = this.elRef.nativeElement;

      const check = () => {
        const clamped = el.scrollHeight > el.clientHeight + 1;
        if (clamped !== this.isClamped()) {
          this.isClamped.set(clamped);
        }
      };

      check();

      this.zone.runOutsideAngular(() => {
        this.ro = new ResizeObserver(check);
        this.ro.observe(el);
      });
    });
  }

  ngOnDestroy(): void {
    this.ro?.disconnect();
  }
}
