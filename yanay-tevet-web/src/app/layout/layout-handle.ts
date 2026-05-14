import {
  ComponentRef,
  createComponent,
  DestroyRef,
  EnvironmentInjector,
  inject,
  Injectable,
  Injector,
  Type,
} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {LayoutService} from './layout-service';
import {BreadcrumbContextChip, BreadcrumbSegment} from './layout-breadcrumb-data';

@Injectable()
export class LayoutHandle {
  private readonly layoutService = inject(LayoutService);
  private readonly env = inject(EnvironmentInjector);
  private readonly injector = inject(Injector);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);

  private readonly owner = Symbol('drawer');
  private readonly depth = this.getActivatedRouteDepth(this.route);
  private ref: ComponentRef<any> = null;

  constructor() {
    this.destroyRef.onDestroy(() => this.clear());
  }

  getActivatedRouteDepth(route: ActivatedRoute): number {
    let depth = 0;
    let r: ActivatedRoute | null = route;
    while (r) {
      depth += 1;
      r = r.parent;
    }
    return depth;
  }

  registerBreadcrumb(segments: BreadcrumbSegment[], contextChip?: BreadcrumbContextChip): void {
    this.layoutService.registerBreadcrumb(this.owner, {depth: this.depth, segments, contextChip});
  }

  registerRightDrawerClass(drawerClass: Type<any>, drawerIcon: string, drawerTitle: string): void {
    this.ref?.destroy();
    if (drawerClass) {
      this.ref = createComponent(drawerClass, {environmentInjector: this.env, elementInjector: this.injector});
    }
    this.layoutService.registerRightDrawer(this.owner, {
      depth: this.depth,
      drawerComponent: this.ref,
      drawerIcon: drawerIcon,
      drawerTitle: drawerTitle,
    });
  }

  clear(): void {
    this.layoutService.unregisterRightDrawer(this.owner);
    this.layoutService.unregisterBreadcrumb(this.owner);
    this.ref?.destroy();
  }
}
