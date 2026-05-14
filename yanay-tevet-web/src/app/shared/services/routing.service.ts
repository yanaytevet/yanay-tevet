import {Injectable, inject} from '@angular/core';
import {Router, UrlTree} from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class RoutingService {
  private router = inject(Router);

  // Contact
  getContactUrl(): UrlTree {
    return this.router.createUrlTree(['/contact']);
  }

  navigateToContact(): Promise<boolean> {
    return this.router.navigateByUrl(this.getContactUrl());
  }

  // FAQ
  getFaqUrl(): UrlTree {
    return this.router.createUrlTree(['/faq']);
  }

  navigateToFaq(): Promise<boolean> {
    return this.router.navigateByUrl(this.getFaqUrl());
  }

  // Terms & Conditions
  getTermsUrl(): UrlTree {
    return this.router.createUrlTree(['/terms']);
  }

  navigateToTerms(): Promise<boolean> {
    return this.router.navigateByUrl(this.getTermsUrl());
  }

  // Privacy Policy
  getPrivacyUrl(): UrlTree {
    return this.router.createUrlTree(['/privacy']);
  }

  navigateToPrivacy(): Promise<boolean> {
    return this.router.navigateByUrl(this.getPrivacyUrl());
  }

  // Home
  getHomeUrl(): UrlTree {
    return this.router.createUrlTree(['/']);
  }

  navigateToHome(): Promise<boolean> {
    return this.router.navigateByUrl(this.getHomeUrl());
  }

  // Login
  getLoginUrl(): UrlTree {
    return this.router.createUrlTree(['/login']);
  }

  navigateToLogin(): Promise<boolean> {
    return this.router.navigateByUrl(this.getLoginUrl());
  }

  // User Settings
  getUserSettingsUrl(): UrlTree {
    return this.router.createUrlTree(['/user-settings']);
  }

  navigateToUserSettings(): Promise<boolean> {
    return this.router.navigateByUrl(this.getUserSettingsUrl());
  }

  // Example routes
  getExampleFormUrl(): UrlTree {
    return this.router.createUrlTree(['/example-form']);
  }

  navigateToExampleForm(): Promise<boolean> {
    return this.router.navigateByUrl(this.getExampleFormUrl());
  }

  getExampleTableUrl(): UrlTree {
    return this.router.createUrlTree(['/example-table']);
  }

  navigateToExampleTable(): Promise<boolean> {
    return this.router.navigateByUrl(this.getExampleTableUrl());
  }

  getExampleDialogsUrl(): UrlTree {
    return this.router.createUrlTree(['/example-dialogs']);
  }

  navigateToExampleDialogs(): Promise<boolean> {
    return this.router.navigate(['/example-dialogs']);
  }

  getExampleWebsocketsUrl(): UrlTree {
    return this.router.createUrlTree(['/example-websockets']);
  }

  navigateToExampleWebsockets(): Promise<boolean> {
    return this.router.navigate(['/example-websockets']);
  }

  getExampleFilesUrl(): UrlTree {
    return this.router.createUrlTree(['/example-files']);
  }

  navigateToExampleFiles(): Promise<boolean> {
    return this.router.navigateByUrl(this.getExampleFilesUrl());
  }

  // Dream Diary
  getDreamDiaryUrl(): UrlTree {
    return this.router.createUrlTree(['/dream-diary']);
  }

  navigateToDreamDiary(): Promise<boolean> {
    return this.router.navigateByUrl(this.getDreamDiaryUrl());
  }
}
