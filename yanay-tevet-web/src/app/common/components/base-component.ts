import {Subscription} from 'rxjs';
import {Component, OnDestroy} from '@angular/core';

@Component({
  template: ''
})
export class BaseComponent implements OnDestroy {
  protected subscriptions: Subscription[] = [];

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }
}
