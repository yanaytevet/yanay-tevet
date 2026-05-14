import {CanActivateFn, Router} from '@angular/router';
import {inject} from '@angular/core';
import {AuthenticationService} from './authentication.service';
import {filter, firstValueFrom} from 'rxjs';
import {toObservable} from '@angular/core/rxjs-interop';

export const loggedInGuard: CanActivateFn = () => {
    const authService = inject(AuthenticationService);
    const router = inject(Router);

    const obs = toObservable(authService.isLoggedIn).pipe(
        filter((val): val is boolean => val !== null)
    );

    return firstValueFrom(obs).then(isLoggedIn => {
        return isLoggedIn ? true : router.createUrlTree(['/login']);
    });
};
