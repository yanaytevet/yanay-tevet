import {computed, Injectable, signal} from '@angular/core';
import {LayoutDrawerData} from './layout-drawer-data';
import {LayoutBreadcrumbData} from './layout-breadcrumb-data';

@Injectable({
  providedIn: 'root',
})
export class LayoutService {
  readonly ownerToBreadcrumbData = signal<Map<symbol, LayoutBreadcrumbData>>(new Map());
  readonly ownerToLayoutRightDrawerData = signal<Map<symbol, LayoutDrawerData>>(new Map());
  readonly isLeftDrawerOpen = signal(false);
  readonly isRightDrawerOpen = signal(false);
  readonly rightDrawerBadge = signal(false);

  readonly currentLayoutRightDrawerData = computed<LayoutDrawerData>(() => {
    const layoutDataArray: LayoutDrawerData[] = Array.from(this.ownerToLayoutRightDrawerData().values());
    layoutDataArray.sort((a, b) => b.depth - a.depth);
    return layoutDataArray[0] ?? null;
  });

  readonly currentBreadcrumbData = computed<LayoutBreadcrumbData>(() => {
    const dataArray: LayoutBreadcrumbData[] = Array.from(this.ownerToBreadcrumbData().values());
    dataArray.sort((a, b) => b.depth - a.depth);
    return dataArray[0] ?? null;
  });

  readonly breadcrumbSegments = computed(() => {
    const data = this.currentBreadcrumbData();
    if (!data || data.segments.length === 0) {
      return [];
    }
    return data.segments;
  });
  readonly breadcrumbParentSegment = computed(() => {
    const segments = this.breadcrumbSegments();
    if (segments.length < 2) {
      return null;
    }
    return segments[0];
  });
  readonly breadcrumbContextChip = computed(() => this.currentBreadcrumbData()?.contextChip ?? null);

  readonly rightDrawerComponent = computed(() => this.currentLayoutRightDrawerData()?.drawerComponent ?? null);
  readonly rightDrawerIcon = computed(() => this.currentLayoutRightDrawerData()?.drawerIcon ?? null);
  readonly rightDrawerTitle = computed(() => this.currentLayoutRightDrawerData()?.drawerTitle ?? null);
  readonly isRightDrawerVisible = computed(() => !!this.rightDrawerComponent());

  readonly isAnyDrawerOpen = computed(() => this.isLeftDrawerOpen() || this.isRightDrawerOpen());

  toggleLeftDrawer() {
    this.isLeftDrawerOpen.update(open => !open);
  }

  toggleRightDrawer() {
    this.isRightDrawerOpen.update(open => !open);
    this.turnOffRightDrawerRedBadge();
  }

  turnOnRightDrawerRedBadge() {
    if (this.isRightDrawerOpen()) {
      return;
    }
    this.rightDrawerBadge.set(true);
  }

  turnOffRightDrawerRedBadge() {
    this.rightDrawerBadge.set(false);
  }

  closeBothDrawers() {
    this.isLeftDrawerOpen.set(false);
    this.isRightDrawerOpen.set(false);
  }

  registerRightDrawer(owner: symbol, layoutDrawerData: LayoutDrawerData) {
    this.ownerToLayoutRightDrawerData.update(map => {
      const newMap = new Map(map);
      newMap.set(owner, layoutDrawerData);
      return newMap;
    });
  }

  unregisterRightDrawer(owner: symbol) {
    this.ownerToLayoutRightDrawerData.update(map => {
      const newMap = new Map(map);
      newMap.delete(owner);
      return newMap;
    });
  }

  registerBreadcrumb(owner: symbol, data: LayoutBreadcrumbData) {
    this.ownerToBreadcrumbData.update(map => {
      const newMap = new Map(map);
      newMap.set(owner, data);
      return newMap;
    });
  }

  unregisterBreadcrumb(owner: symbol) {
    this.ownerToBreadcrumbData.update(map => {
      const newMap = new Map(map);
      newMap.delete(owner);
      return newMap;
    });
  }
}
