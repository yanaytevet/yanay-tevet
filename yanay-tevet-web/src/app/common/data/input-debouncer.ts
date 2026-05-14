import { debounceTime, distinctUntilChanged, Subscription } from 'rxjs';
import { Observable, Subject } from 'rxjs';
import { FormControl } from '@angular/forms';

export class InputDebounce<T> {
  private readonly subs = new Subscription();

  private readonly valueChangedSub = new Subject<T>();
  readonly valueChangedFinishedSub = new Subject<T>();

  readonly valueChangedFinished$: Observable<T> =
    this.valueChangedFinishedSub.asObservable();

  value: T | null = null;
  readonly ctrl = new FormControl<T | null>(null);

  constructor(initValue?: T, debounceTimeMs = 500) {
    this.subs.add(
      this.valueChangedSub.pipe(
        debounceTime(debounceTimeMs),
        distinctUntilChanged(),
      ).subscribe((newValue) => {
        this.value = newValue;
        this.valueChangedFinishedSub.next(newValue);
      }),
    );

    this.subs.add(
      this.ctrl.valueChanges.subscribe((event) => {
        // event is T | null
        this.onValueChangedInCtrl(event as T);
      }),
    );

    if (initValue !== undefined) {
      this.setValueWithoutTrigger(initValue);
    }
  }

  onValueChangedInCtrl(newValue: T): void {
    this.valueChangedSub.next(newValue);
  }

  setValue(newValue: T): void {
    this.ctrl.setValue(newValue);
  }

  setValueImmediately(newValue: T): void {
    this.ctrl.setValue(newValue, { emitEvent: false });
    this.value = newValue;
    this.valueChangedFinishedSub.next(newValue);
  }

  setValueWithoutTrigger(newValue: T): void {
    if (this.value === newValue) {
      return;
    }
    this.ctrl.setValue(newValue, { emitEvent: false });
    this.value = newValue;
  }

  destroy(): void {
    this.subs.unsubscribe();       // ✅ stops subscriptions
    this.valueChangedSub.complete();
    this.valueChangedFinishedSub.complete();
  }
}
