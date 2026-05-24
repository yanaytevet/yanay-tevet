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

  getDreamDiaryNewEntryUrl(): UrlTree {
    return this.router.createUrlTree(['/dream-diary/new']);
  }

  navigateToDreamDiaryNewEntry(): Promise<boolean> {
    return this.router.navigateByUrl(this.getDreamDiaryNewEntryUrl());
  }

  getDreamDiaryEditEntryUrl(entryId: number): UrlTree {
    return this.router.createUrlTree(['/dream-diary/edit', entryId]);
  }

  navigateToDreamDiaryEditEntry(entryId: number): Promise<boolean> {
    return this.router.navigateByUrl(this.getDreamDiaryEditEntryUrl(entryId));
  }

  // Genre Trainer
  getGenreTrainerUrl(): UrlTree {
    return this.router.createUrlTree(['/genre-trainer']);
  }

  navigateToGenreTrainer(): Promise<boolean> {
    return this.router.navigateByUrl(this.getGenreTrainerUrl());
  }

  // Japanese
  getJapaneseHomeUrl(): UrlTree {
    return this.router.createUrlTree(['/japanese']);
  }

  navigateToJapaneseHome(): Promise<boolean> {
    return this.router.navigateByUrl(this.getJapaneseHomeUrl());
  }

  getJapaneseNodeUrl(nodeId: number): UrlTree {
    return this.router.createUrlTree(['/japanese/node', nodeId]);
  }

  navigateToJapaneseNode(nodeId: number): Promise<boolean> {
    return this.router.navigateByUrl(this.getJapaneseNodeUrl(nodeId));
  }

  getJapaneseIngestUrl(): UrlTree {
    return this.router.createUrlTree(['/japanese/ingest']);
  }

  navigateToJapaneseIngest(): Promise<boolean> {
    return this.router.navigateByUrl(this.getJapaneseIngestUrl());
  }

  getJapaneseReviewUrl(): UrlTree {
    return this.router.createUrlTree(['/japanese/review']);
  }

  navigateToJapaneseReview(): Promise<boolean> {
    return this.router.navigateByUrl(this.getJapaneseReviewUrl());
  }
}
