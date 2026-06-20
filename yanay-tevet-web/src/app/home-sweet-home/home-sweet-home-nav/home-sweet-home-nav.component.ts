import {Component, inject} from '@angular/core';
import {RouterLink, RouterLinkActive} from '@angular/router';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-home-sweet-home-nav',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './home-sweet-home-nav.component.html',
})
export class HomeSweetHomeNavComponent {
  protected readonly routingService = inject(RoutingService);
}
