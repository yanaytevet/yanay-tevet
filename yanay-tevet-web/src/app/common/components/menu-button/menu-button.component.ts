import {Component, input} from '@angular/core';
import {CdkMenuModule} from '@angular/cdk/menu';
import {Action} from '../../interfaces/util/action';
import {NgIcon} from '@ng-icons/core';

export const SEPARATOR = 'SEPARATOR';
export type MenuItem = Action | typeof SEPARATOR;

@Component({
  selector: 'app-menu-button',
  imports: [
    CdkMenuModule,
    NgIcon,
  ],
  templateUrl: './menu-button.component.html',
  styleUrl: './menu-button.component.css'
})
export class MenuButtonComponent {
  text = input<string>('');
  color = input<string>('writing');
  icon = input<string>(null);
  actions= input<MenuItem[]>();

  // Make SEPARATOR constant accessible in the template
  readonly SEPARATOR = SEPARATOR;
}
