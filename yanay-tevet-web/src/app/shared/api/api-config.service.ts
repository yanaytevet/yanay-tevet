import {inject, Injectable} from '@angular/core';
import {client as authClient} from '../../../generated-files/auth/client.gen';
import {client as api_usersClient} from '../../../generated-files/api/users/client.gen';
import {client as api_configurationsClient} from '../../../generated-files/api/configurations/client.gen';
import {client as api_blocksClient} from '../../../generated-files/api/blocks/client.gen';
import {client as api_dreamdiaryClient} from '../../../generated-files/api/dream-diary/client.gen';
import {client as api_genretrainerClient} from '../../../generated-files/api/genre-trainer/client.gen';
import {client as api_japaneseClient} from '../../../generated-files/api/japanese/client.gen';
import {client as api_mydashboardClient} from '../../../generated-files/api/my-dashboard/client.gen';
import {client as api_apartmenthuntClient} from '../../../generated-files/api/apartment-hunt/client.gen';
import {client as api_itinerarylistsClient} from '../../../generated-files/api/itinerary-lists/client.gen';
import {client as api_taskmanagementClient} from '../../../generated-files/api/task-management/client.gen';
import {client as api_workoutplanClient} from '../../../generated-files/api/workout-plan/client.gen';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {environment} from '../../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class ApiConfigService {
    readonly clients = [authClient, api_usersClient, api_configurationsClient, api_blocksClient, api_dreamdiaryClient, api_genretrainerClient, api_japaneseClient, api_mydashboardClient, api_apartmenthuntClient, api_itinerarylistsClient, api_taskmanagementClient, api_workoutplanClient];
    authService = inject(AuthenticationService);

  getBaseUrl(): string {
    return environment.apiUrl;
  }

    initialize(): void {
        this.clients.forEach((client) => {
            client.setConfig({
                baseURL: this.getBaseUrl(),
                withCredentials: true,
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            client.instance.interceptors.request.use(req => {
                if (this.authService.accessToken()) {
                    req.headers.set('Authorization', `Bearer ${this.authService.accessToken()}`);
                }
                return req;
            });
            client.instance.interceptors.response.use(
                response => response,
                async error => {
                    const originalRequest = error.config;
                    if (error.response?.status === 401 && !originalRequest._retry) {
                        originalRequest._retry = true;
                        await this.authService.checkAuth();
                        const newToken = this.authService.accessToken?.();
                        if (newToken) {
                            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
                        }
                        return client.instance(originalRequest);
                    }

                    return Promise.reject(error);
                });
        });
    }
}
