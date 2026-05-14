import {ComponentRef} from '@angular/core';

export interface LayoutDrawerData {
  depth: number
  drawerTitle: string;
  drawerIcon: string;
  drawerComponent: ComponentRef<any>;
}
