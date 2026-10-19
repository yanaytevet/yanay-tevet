import {
  afterRenderEffect,
  Component,
  computed,
  contentChildren,
  effect,
  ElementRef,
  HostListener,
  inject,
  input,
  output,
  signal,
  untracked,
  viewChild
} from '@angular/core';
import {NgIcon} from "@ng-icons/core";
import {ActivatedRoute, Router, RouterLink, RouterLinkActive} from '@angular/router';
import {toSignal} from '@angular/core/rxjs-interop';
import {Tab} from '../tab/tab';
import {NgTemplateOutlet} from '@angular/common';
import {featherChevronLeft, featherChevronRight} from '@ng-icons/feather-icons';

// In-page tabs (DESIGN.md §5, Tabs). The current tab lives in a query param so it survives a reload and can be
// linked to; `tabChange` tells the page which tab is showing, including the one it opens on.
@Component({
  selector: 'app-tabs-group',
  imports: [
    NgIcon,
    NgTemplateOutlet,
    RouterLink,
    RouterLinkActive,
  ],
  templateUrl: './tabs-group.html',
})
export class TabsGroup {
  router = inject(Router);
  route = inject(ActivatedRoute);

  readonly tabs = contentChildren(Tab);
  tabsQueryParam = input<string>('tab');
  readonly tabChange = output<string>();

  private readonly queryParams = toSignal(this.route.queryParams);

  readonly scrollContainer = viewChild<ElementRef<HTMLDivElement>>('scrollContainer');
  readonly canScrollLeft = signal(false);
  readonly canScrollRight = signal(false);

  protected readonly featherChevronLeft = featherChevronLeft;
  protected readonly featherChevronRight = featherChevronRight;

  readonly currentTab = computed<Tab>(() => {
    const firstTab: Tab = this.tabs().filter(tab => !tab.link())[0];
    const tabName = this.queryParams()?.[this.tabsQueryParam()];
    if (!tabName) {
      return firstTab ?? null;
    }
    return this.tabs().find(tab => tab.name() === tabName) ?? firstTab;
  });

  readonly isCurrent = computed<Record<string, boolean>>(() =>
    Object.fromEntries(this.tabs().map(tab => [tab.name(), this.currentTab()?.name() === tab.name()])));

  constructor() {
    // After render, so the tabs are laid out before their width is measured.
    afterRenderEffect(() => {
      this.tabs();
      this.scrollContainer();
      this.checkScroll();
    });

    effect(() => {
      const name = this.currentTab()?.name();
      if (name) {
        untracked(() => this.tabChange.emit(name));
      }
    });
  }

  @HostListener('window:resize')
  onResize() {
    this.checkScroll();
  }

  // scrollLeft runs from 0 towards negative values in a right-to-left container, so "can scroll left" means
  // different things in the two directions.
  checkScroll() {
    const element = this.scrollContainer()?.nativeElement;
    if (!element) {
      return;
    }

    const offset = Math.abs(element.scrollLeft);
    const atStart = offset <= 0;
    const atEnd = offset + element.clientWidth >= element.scrollWidth - 1;
    const isRtl = getComputedStyle(element).direction === 'rtl';
    this.canScrollLeft.set(isRtl ? !atEnd : !atStart);
    this.canScrollRight.set(isRtl ? !atStart : !atEnd);
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
