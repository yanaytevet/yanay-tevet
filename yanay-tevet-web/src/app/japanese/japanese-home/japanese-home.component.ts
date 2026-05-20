import {Component} from '@angular/core';
import {TabsGroup} from '../../common/components/tabs/tabs-group/tabs-group';
import {Tab} from '../../common/components/tabs/tab/tab';
import {JapaneseExploreGridComponent} from '../shared/japanese-explore-grid/japanese-explore-grid.component';
import {JapaneseNavComponent} from '../shared/japanese-nav/japanese-nav.component';

@Component({
  selector: 'app-japanese-home',
  standalone: true,
  imports: [TabsGroup, Tab, JapaneseExploreGridComponent, JapaneseNavComponent],
  templateUrl: './japanese-home.component.html',
})
export class JapaneseHomeComponent {}
