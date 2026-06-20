import {CanActivateFn, Router} from '@angular/router';
import {inject} from '@angular/core';
import {AuthenticationService} from './authentication.service';
import {filter, firstValueFrom} from 'rxjs';
import {toObservable} from '@angular/core/rxjs-interop';
import {Permissions} from '../../../generated-files/auth';

export function hasPermissionGuard(permission: Permissions): CanActivateFn {
    return (_route, state) => {
        const authService = inject(AuthenticationService);
        const router = inject(Router);

        const obs = toObservable(authService.isLoggedIn).pipe(
            filter((val): val is boolean => val !== null)
        );

        return firstValueFrom(obs).then(isLoggedIn => {
            if (!isLoggedIn) {
                return router.createUrlTree(['/login'], {queryParams: {redirect: state.url}});
            }
            const user = authService.user();
            const hasPermission = user?.is_admin || user?.permissions?.includes(permission);
            return hasPermission ? true : router.createUrlTree(['/']);
        });
    };
}
