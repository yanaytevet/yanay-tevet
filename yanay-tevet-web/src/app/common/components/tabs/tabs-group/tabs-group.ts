import {
  Component,
  computed,
  contentChildren,
  effect,
  ElementRef,
  HostListener,
  inject,
  input,
  signal,
  viewChild
} from '@angular/core';
import {NgIcon} from "@ng-icons/core";
import {ActivatedRoute, Router, RouterLink} from '@angular/router';
import {toSignal} from '@angular/core/rxjs-interop';
import {Tab} from '../tab/tab';
import {NgTemplateOutlet} from '@angular/common';
import {heroChevronLeft, heroChevronRight} from "@ng-icons/heroicons/outline";

@Component({
  selector: 'app-tabs-group',
  imports: [
    NgIcon,
    NgTemplateOutlet,
    RouterLink
  ],
  templateUrl: './tabs-group.html',
  styleUrl: './tabs-group.css'
})
export class TabsGroup {
  router = inject(Router);
  route = inject(ActivatedRoute);

  readonly tabs = contentChildren(Tab);
  tabsQueryParam = input<string>('tab');

  private readonly queryParams = toSignal(this.route.queryParams);

  readonly scrollContainer = viewChild<ElementRef<HTMLDivElement>>('scrollContainer');
  readonly canScrollLeft = signal(false);
  readonly canScrollRight = signal(false);

  protected readonly heroChevronLeft = heroChevronLeft;
  protected readonly heroChevronRight = heroChevronRight;

  constructor() {
    effect(() => {
      if (this.scrollContainer()) {
        this.checkScroll();
      }
    });

    effect(() => {
      this.tabs();
      this.checkScroll();
    });
  }

  readonly currentTab = computed<Tab>(() => {
    const firstTab: Tab = this.tabs().filter(tab => !tab.link())[0];
    const tabName = this.queryParams()?.[this.tabsQueryParam()];
    if (!tabName) {
      return firstTab ?? null;
    }
    return this.tabs().find(tab => tab.name() === tabName) ?? firstTab;
  });

  @HostListener('window:resize')
  onResize() {
    this.checkScroll();
  }

  checkScroll() {
    const element = this.scrollContainer()?.nativeElement;
    if (!element) {
      return;
    }

    this.canScrollLeft.set(element.scrollLeft > 0);
    this.canScrollRight.set(
      element.scrollLeft + element.clientWidth < element.scrollWidth - 1
    );
  }

  scroll(direction: 'left' | 'right') {
    const element = this.scrollContainer()?.nativeElement;
    if (!element) {
      return;
    }

    const scrollAmount = element.clientWidth * 0.8;
    element.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth'
    });
  }

  async tabClicked(tab: Tab) {
    await this.router.navigate([], {
      queryParams: {[this.tabsQueryParam()]: tab.name()},
      queryParamsHandling: 'merge',
    });
  }

}
