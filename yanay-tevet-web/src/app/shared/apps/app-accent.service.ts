import {effect, inject, Injectable, signal} from '@angular/core';
import {DOCUMENT} from '@angular/common';
import {NavigationEnd, Router} from '@angular/router';
import {HubApp, hubAppForUrl} from './hub-apps';

// Puts the current app's key on <html data-app="…"> so the accent tokens follow it everywhere, dialogs
// in the CDK overlay included. Pages outside any app (home, settings, admin) keep the hub's blue.
@Injectable({
  providedIn: 'root'
})
export class AppAccentService {
  private readonly router = inject(Router);
  private readonly document = inject(DOCUMENT);

  readonly currentApp = signal<HubApp | null>(hubAppForUrl(this.router.url));

  constructor() {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.currentApp.set(hubAppForUrl(event.urlAfterRedirects));
      }
    });

    effect(() => {
      const app = this.currentApp();
      const htmlElement = this.document.documentElement;
      if (app) {
        htmlElement.dataset['app'] = app.key;
      } else {
        delete htmlElement.dataset['app'];
      }
    });
  }
}
