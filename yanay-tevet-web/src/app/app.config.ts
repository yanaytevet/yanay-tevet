import {ApplicationConfig, ErrorHandler, inject, provideAppInitializer, provideZoneChangeDetection} from '@angular/core';
import {provideRouter, withNavigationErrorHandler} from '@angular/router';
import {provideLottieOptions} from 'ngx-lottie';
import player from 'lottie-web';

import {routes} from './app.routes';
import {ApiConfigService} from './shared/api/api-config.service';
import {GlobalConfigurationsService} from './shared/services/global-configurations.service';
import {provideHttpClient} from '@angular/common/http';
import {AuthenticationService} from './common/authentication/authentication.service';
import {DarkModeService} from './common/services/dark-mode.service';
import {VersionCheckService} from './common/services/version-check.service';
import {ChunkLoadErrorHandler, handleChunkLoadNavigationError} from './common/errors/chunk-load-error-handler';

export const appConfig: ApplicationConfig = {
    providers: [
        provideZoneChangeDetection({eventCoalescing: true}),
        provideLottieOptions({player: () => player}),
        provideHttpClient(),
        provideRouter(routes, withNavigationErrorHandler(handleChunkLoadNavigationError)),
        {provide: ErrorHandler, useClass: ChunkLoadErrorHandler},
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
        }),
        provideAppInitializer(() => {
            inject(VersionCheckService);
        })
    ]
};
