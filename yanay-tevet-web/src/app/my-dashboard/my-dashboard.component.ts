import {Component, inject} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {bootstrapArrowClockwise} from '@ng-icons/bootstrap-icons';
import {MyDashboardService} from './my-dashboard.service';
import {OpenAiCreditsCardComponent} from './openai-credits-card/openai-credits-card.component';

@Component({
  selector: 'app-my-dashboard',
  standalone: true,
  imports: [NgIcon, OpenAiCreditsCardComponent],
  providers: [MyDashboardService],
  templateUrl: './my-dashboard.component.html',
})
export class MyDashboardComponent {
  protected readonly service = inject(MyDashboardService);
  protected readonly bootstrapArrowClockwise = bootstrapArrowClockwise;

  refreshAll(): void {
    this.service.refreshAll();
  }
}
