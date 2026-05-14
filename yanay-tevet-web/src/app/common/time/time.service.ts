import {Injectable, signal} from '@angular/core';
import {parseISO} from 'date-fns';
import {formatInTimeZone} from 'date-fns-tz';

@Injectable({providedIn: 'root'})
export class TimeService {
  readonly timezone = signal<string>(Intl.DateTimeFormat().resolvedOptions().timeZone);

  format(dateStr: string | null | undefined, pattern = "MMM d, yyyy HH:mm ('UTC' xxx)"): string | null {
    if (!dateStr) {
      return null;
    }
    return formatInTimeZone(parseISO(dateStr), this.timezone(), pattern);
  }
}
