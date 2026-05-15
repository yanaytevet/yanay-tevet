import {Component} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherX} from '@ng-icons/feather-icons';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';

@Component({
  selector: 'app-view-image-dialog',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({featherX})],
  templateUrl: './view-image-dialog.component.html',
})
export class ViewImageDialogComponent extends BaseDialogComponent<string, null> {
  readonly featherX = featherX;
}
