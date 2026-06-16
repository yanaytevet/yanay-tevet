import {ApplicationConfig, inject, provideAppInitializer, provideZoneChangeDetection} from '@angular/core';
import {provideRouter} from '@angular/router';
import {provideLottieOptions} from 'ngx-lottie';
import player from 'lottie-web';

import {routes} from './app.routes';
import {ApiConfigService} from './shared/api/api-config.service';
import {GlobalConfigurationsService} from './shared/services/global-configurations.service';
import {provideHttpClient} from '@angular/common/http';
import {AuthenticationService} from './common/authentication/authentication.service';
import {DarkModeService} from './common/services/dark-mode.service';

export const appConfig: ApplicationConfig = {
    providers: [
        provideZoneChangeDetection({eventCoalescing: true}),
        provideLottieOptions({player: () => player}),
        provideHttpClient(),
        provideRouter(routes),
        provideAppInitializer(() => {
            const apiConfigService = inject(ApiConfigService);
            return apiConfigService.initialize();
        }),
        provideAppInitializer(async () => {
            const authService = inject(AuthenticationService);
            await authService.checkAuth();
        }),
        provideAppInitializer(async () => {
            const configService = inject(GlobalConfigurationsService);
            await configService.loadConfigurations();
        }),
        provideAppInitializer(() => {
            inject(DarkModeService);
        })
    ]
};
