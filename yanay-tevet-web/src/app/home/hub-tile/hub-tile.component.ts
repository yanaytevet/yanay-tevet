import {Component, input} from '@angular/core';
import {RouterLink, UrlTree} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {HubAppKey} from '../../shared/apps/hub-apps';

export interface HubTileApp {
  name: string;
  icon: string;
  // The app whose accent the tile borrows; null keeps the hub's blue.
  key: HubAppKey | null;
}

@Component({
  selector: 'app-hub-tile',
  imports: [RouterLink, NgIcon],
  templateUrl: './hub-tile.component.html',
  host: {class: 'block'},
})
export class HubTileComponent {
  readonly app = input.required<HubTileApp>();
  readonly url = input.required<UrlTree>();
  readonly description = input.required<string>();
}
