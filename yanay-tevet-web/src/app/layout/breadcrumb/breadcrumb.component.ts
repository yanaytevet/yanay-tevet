import {Component, inject} from '@angular/core';
import {RouterLink} from '@angular/router';
import {LayoutService} from '../layout-service';

@Component({
  selector: 'app-breadcrumb',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './breadcrumb.component.html',
})
export class BreadcrumbComponent {
  protected readonly layoutService = inject(LayoutService);
}
