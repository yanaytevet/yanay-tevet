import {Component, inject, signal} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {RouterLink} from '@angular/router';
import {ingestNodeView} from '../../../generated-files/api/japanese';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-japanese-ingest',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './japanese-ingest.component.html',
})
export class JapaneseIngestComponent {
  private readonly dialogService = inject(DialogService);
  protected readonly routingService = inject(RoutingService);

  readonly text = signal<string>('');
  readonly isWorking = signal<boolean>(false);

  async onSubmit(): Promise<void> {
    const text = this.text().trim();
    if (!text) {
      return;
    }
    this.isWorking.set(true);
    try {
      const res = await ingestNodeView({body: {text}});
      await this.routingService.navigateToJapaneseNode(res.data.id);
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to ingest: ${err}`,
      });
    } finally {
      this.isWorking.set(false);
    }
  }
}
