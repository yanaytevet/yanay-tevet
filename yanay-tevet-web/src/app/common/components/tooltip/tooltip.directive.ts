import {Directive, ElementRef, HostListener, input, Renderer2, OnDestroy, inject} from '@angular/core';
import {createPopper, Instance} from '@popperjs/core';

@Directive({
  selector: '[appTooltip]',
})
export class TooltipDirective implements OnDestroy {
  private el = inject(ElementRef);
  private renderer = inject(Renderer2);
  text = input.required<string>({alias: 'appTooltip'});
  private tooltipEl?: HTMLElement;
  private popper?: Instance;

  @HostListener('mouseenter')
  @HostListener('focus')
  show() {
    const content = this.text();
    if (!content) return;

    this.hide();

    this.tooltipEl = this.renderer.createElement('span');
    this.tooltipEl.textContent = content;
    this.renderer.addClass(this.tooltipEl, 'tooltip-box');
    document.body.appendChild(this.tooltipEl);

    this.popper = createPopper(this.el.nativeElement, this.tooltipEl, {
      placement: 'top',
      modifiers: [
        {name: 'offset', options: {offset: [0, 8]}},
        {name: 'preventOverflow', options: {padding: 8}},
        {name: 'flip', options: {fallbackPlacements: ['top', 'bottom', 'right', 'left']}}
      ]
    });
  }

  @HostListener('mouseleave')
  @HostListener('blur')
  @HostListener('click')
  @HostListener('mousedown')
  hide() {
    if (this.popper) {
      this.popper.destroy();
      this.popper = undefined;
    }
    if (this.tooltipEl) {
      document.body.removeChild(this.tooltipEl);
      this.tooltipEl = undefined;
    }
  }

  ngOnDestroy() {
    this.hide();
  }
}
