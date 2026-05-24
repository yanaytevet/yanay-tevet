import {Injectable, signal} from '@angular/core';

@Injectable()
export class MyDashboardService {
  // Incrementing this signal asks every registered card to re-fetch.
  // Cards subscribe via an effect and call their own load() when it changes.
  readonly refreshTick = signal(0);

  refreshAll(): void {
    this.refreshTick.update(n => n + 1);
  }
}
