import {CanActivateFn, Router} from '@angular/router';
import {inject} from '@angular/core';
import {filter, firstValueFrom} from 'rxjs';
import {toObservable} from '@angular/core/rxjs-interop';
import {AuthenticationService} from '../common/authentication/authentication.service';
import {RoutingService} from '../shared/services/routing.service';

// Sends a user landing on /home-sweet-home to the first sub-app they can access,
// so friends with only the Villa Villekulla permission aren't dropped on Apartment Hunt.
export const homeSweetHomeRedirectGuard: CanActivateFn = () => {
  const authService = inject(AuthenticationService);
  const routingService = inject(RoutingService);
  const router = inject(Router);

  const obs = toObservable(authService.isLoggedIn).pipe(
    filter((val): val is boolean => val !== null),
  );

  return firstValueFrom(obs).then(() => {
    if (authService.hasPermission('apartment_hunt')) {
      return routingService.getApartmentHuntUrl();
    }
    if (authService.hasPermission('villa_villekulla')) {
      return routingService.getVillaVillekullaUrl();
    }
    if (authService.hasPermission('renters_crm')) {
      return routingService.getRentersCrmUrl();
    }
    return router.createUrlTree(['/']);
  });
};
