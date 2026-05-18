import {inject, Injectable} from '@angular/core';
import {GlobalConfigurationsService} from '../../shared/services/global-configurations.service';

interface CodeClient {
  requestCode(): void;
}

interface CodeResponse {
  code?: string;
  error?: string;
}

declare const google: {
  accounts: {
    oauth2: {
      initCodeClient(config: {
        client_id: string;
        scope: string;
        ux_mode: 'popup' | 'redirect';
        callback: (response: CodeResponse) => void;
      }): CodeClient;
    };
  };
};

@Injectable({providedIn: 'root'})
export class GoogleAuthService {
  private readonly globalConfigurationsService = inject(GlobalConfigurationsService);
  private scriptLoadPromise: Promise<void> | null = null;

  private loadScript(): Promise<void> {
    if (typeof google !== 'undefined' && google?.accounts?.oauth2) {
      return Promise.resolve();
    }
    if (this.scriptLoadPromise) {
      return this.scriptLoadPromise;
    }
    this.scriptLoadPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Google Sign-In script'));
      document.head.appendChild(script);
    });
    return this.scriptLoadPromise;
  }

  async signIn(): Promise<string> {
    await this.loadScript();
    return new Promise((resolve, reject) => {
      const client = google.accounts.oauth2.initCodeClient({
        client_id: this.globalConfigurationsService.googleClientId(),
        scope: 'openid email profile',
        ux_mode: 'popup',
        callback: (response) => {
          if (response.code) {
            resolve(response.code);
          } else {
            reject(new Error(response.error ?? 'No authorization code received'));
          }
        },
      });
      client.requestCode();
    });
  }
}
