import {Component, inject} from '@angular/core';
import {RouterLink, RouterLinkActive} from '@angular/router';
import {AuthenticationService} from '../../../common/authentication/authentication.service';
import {RoutingService} from '../../../shared/services/routing.service';

@Component({
  selector: 'app-japanese-nav',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './japanese-nav.component.html',
})
export class JapaneseNavComponent {
  protected readonly authService = inject(AuthenticationService);
  protected readonly routingService = inject(RoutingService);
}
