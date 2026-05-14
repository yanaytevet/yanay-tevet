import {inject, Pipe, PipeTransform} from '@angular/core';
import {TimeService} from './time.service';

@Pipe({
  name: 'formatTime',
  standalone: true,
  pure: false,
})
export class FormatTimePipe implements PipeTransform {
  private readonly timeService = inject(TimeService);

  transform(value: string | null | undefined, pattern?: string): string | null {
    return this.timeService.format(value, pattern);
  }
}
