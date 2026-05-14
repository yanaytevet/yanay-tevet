import {Component, input, TemplateRef, viewChild} from '@angular/core';
import {UrlTree} from '@angular/router';

@Component({
  selector: 'app-tab',
  imports: [],
  template: `
    <ng-template #contentTpl>
      <ng-content/>
    </ng-template>
  `,
})
export class Tab {
  public name = input.required<string>();
  public label = input.required<string>();
  public icon = input<string>(null);
  public link = input<string| string[] | UrlTree>(null);

  readonly contentTpl = viewChild<TemplateRef<unknown>>('contentTpl');
}
