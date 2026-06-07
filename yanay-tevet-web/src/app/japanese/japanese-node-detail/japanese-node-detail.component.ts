import {Component, computed, inject, signal} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {DomSanitizer, SafeHtml} from '@angular/platform-browser';
import {Subscription} from 'rxjs';
import {
  approveNodeView,
  generateContentView,
  readNodeView,
  updateNodeTitleView,
  NodeDetailSchema,
  EdgeType,
  IncomingEdgeSchema,
  OutgoingEdgeSchema,
} from '../../../generated-files/api/japanese';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {BasePageComponent} from '../../common/components/base-page-component';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {UserWebsocketsService} from '../../common/services/user-websockets.service';
import {WebsocketEvent} from '../../common/interfaces/websockets/websocket-event';
import {RoutingService} from '../../shared/services/routing.service';
import {FuriganaComponent} from '../shared/furigana/furigana.component';
import {JapaneseNavComponent} from '../shared/japanese-nav/japanese-nav.component';
import {NodeSummaryCardComponent} from '../shared/node-summary-card/node-summary-card.component';
import {SpeakButtonComponent} from '../shared/speak-button/speak-button.component';

const EDGE_TYPE_LABELS: Record<EdgeType, string> = {
  contains: 'Contains',
  composed_of: 'Composed of',
  uses_rule: 'Uses rule',
  example_of: 'Example of',
  exception_to: 'Exception to',
  synonym_of: 'Synonym of',
  related_to: 'Related',
  same_kanji_as: 'Same kanji as',
};

const INCOMING_EDGE_TYPE_LABELS: Record<EdgeType, string> = {
  contains: 'Used in sentences',
  composed_of: 'Used in words',
  uses_rule: 'Sentences using this rule',
  example_of: 'Examples',
  exception_to: 'Exceptions',
  synonym_of: 'Synonyms',
  related_to: 'Related',
  same_kanji_as: 'Same kanji as',
};

@Component({
  selector: 'app-japanese-node-detail',
  standalone: true,
  imports: [FuriganaComponent, JapaneseNavComponent, NodeSummaryCardComponent, SpeakButtonComponent],
  templateUrl: './japanese-node-detail.component.html',
})
export class JapaneseNodeDetailComponent extends BasePageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly sanitizer = inject(DomSanitizer);
  private readonly dialogService = inject(DialogService);
  private readonly routingService = inject(RoutingService);
  private readonly userWebsocketsService = inject(UserWebsocketsService);
  protected readonly authService = inject(AuthenticationService);

  private currentNodeId: number | null = null;
  private nodeWsSubscription: Subscription | null = null;

  readonly node = signal<NodeDetailSchema | null>(null);
  readonly isLoading = signal<boolean>(true);
  readonly isWorking = signal<boolean>(false);
  readonly error = signal<string | null>(null);

  readonly statusClass = computed(() => {
    const node = this.node();
    if (!node) {
      return '';
    }
    switch (node.status) {
      case 'published':
        return 'bg-emerald-100 text-emerald-700';
      case 'needs_review':
        return 'bg-amber-100 text-amber-700';
      case 'generating':
        return 'bg-sky-100 text-sky-700';
      default:
        return 'bg-secondary-100 text-secondary-500';
    }
  });

  readonly statusLabel = computed(() => this.node()?.status?.replace(/_/g, ' ') ?? '');

  readonly nodeTitle = computed<string>(() => {
    const node = this.node();
    if (!node) {
      return '';
    }
    return (
      node.sentence_data?.japanese ??
      node.word_data?.base_form ??
      node.kanji_data?.character ??
      node.particle_data?.particle ??
      node.rule_data?.name ??
      ''
    );
  });

  readonly contentHtml = computed<SafeHtml>(() => {
    const node = this.node();
    if (!node || !node.content_html) {
      return '';
    }
    const withFurigana = node.content_html.replace(
      /([一-龯㐀-䶿]+)\(([぀-ゟー]+)\)/g,
      '<ruby>$1<rt class="furigana-rt">$2</rt></ruby>',
    );
    return this.sanitizer.bypassSecurityTrustHtml(withFurigana);
  });

  readonly outgoingGroups = computed<{label: string; edges: OutgoingEdgeSchema[]}[]>(() => {
    const node = this.node();
    if (!node) {
      return [];
    }
    const buckets = new Map<EdgeType, OutgoingEdgeSchema[]>();
    for (const edge of node.outgoing_edges) {
      const existing = buckets.get(edge.edge_type) ?? [];
      existing.push(edge);
      buckets.set(edge.edge_type, existing);
    }
    return [...buckets.entries()].map(([type, edges]) => ({
      label: EDGE_TYPE_LABELS[type],
      edges,
    }));
  });

  readonly incomingGroups = computed<{label: string; edges: IncomingEdgeSchema[]}[]>(() => {
    const node = this.node();
    if (!node) {
      return [];
    }
    const buckets = new Map<EdgeType, IncomingEdgeSchema[]>();
    for (const edge of node.incoming_edges) {
      const existing = buckets.get(edge.edge_type) ?? [];
      existing.push(edge);
      buckets.set(edge.edge_type, existing);
    }
    return [...buckets.entries()].map(([type, edges]) => ({
      label: INCOMING_EDGE_TYPE_LABELS[type],
      edges,
    }));
  });

  constructor() {
    super();
    this.subscriptions.push(this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        void this.load(id);
        void this.subscribeToNode(id);
      }
    }));
  }

  private async load(id: number): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      const res = await readNodeView({path: {object_id: id}});
      this.node.set(res.data);
    } catch {
      this.error.set('Node not found.');
      this.node.set(null);
    } finally {
      this.isLoading.set(false);
    }
  }

  private async subscribeToNode(id: number): Promise<void> {
    this.currentNodeId = id;
    this.nodeWsSubscription?.unsubscribe();
    await this.userWebsocketsService.finishedConnecting();
    if (this.currentNodeId !== id) {
      return;
    }
    this.nodeWsSubscription = await this.userWebsocketsService.websocketGroupSubscribe(
      'japanese_node',
      {node_id: id},
      (event: WebsocketEvent) => this.onNodeEvent(id, event),
    );
    this.subscriptions.push(this.nodeWsSubscription);
  }

  private onNodeEvent(subscribedId: number, event: WebsocketEvent): void {
    const updated = event.payload as unknown as NodeDetailSchema;
    this.isWorking.set(false);
    if (updated.id === subscribedId) {
      this.node.set(updated);
    } else {
      void this.routingService.navigateToJapaneseNode(updated.id);
    }
  }

  async generate(): Promise<void> {
    const node = this.node();
    if (!node) {
      return;
    }

    const userNote = await this.dialogService.getTextFromInputDialog({
      title: 'Generate content',
      text: 'Optional notes to guide the model (e.g. "use the kanji form 中", "treat this as a noun, not a verb", "this is the polite copula"). Leave empty to generate with the default rules.',
      label: 'Notes (optional)',
      isTextArea: true,
      textAreaRows: 5,
      allowEmpty: true,
      confirmActionName: 'Generate',
    });
    if (userNote === null) {
      return;
    }

    this.isWorking.set(true);
    try {
      await generateContentView({
        body: {user_note: userNote.trim() === '' ? null : userNote},
        path: {object_id: node.id},
      });
      // Generation runs in the background on the server; the finished node is pushed
      // over the websocket (see onNodeEvent), which also clears the working state.
      this.node.update(n => (n ? {...n, status: 'generating'} : n));
    } catch (err) {
      this.isWorking.set(false);
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to generate content: ${err}`,
      });
    }
  }

  async editTitle(): Promise<void> {
    const node = this.node();
    if (!node) {
      return;
    }
    const title = await this.dialogService.getTextFromInputDialog({
      title: 'Edit title',
      text: 'Update the main text shown for this node. For words and sentences you can include furigana like 漢字(かんじ).',
      label: 'Title',
      defaultValue: this.nodeTitle(),
      confirmActionName: 'Save',
    });
    if (title === null) {
      return;
    }
    this.isWorking.set(true);
    try {
      const res = await updateNodeTitleView({body: {title}, path: {object_id: node.id}});
      this.node.set(res.data);
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to update title: ${err}`,
      });
    } finally {
      this.isWorking.set(false);
    }
  }

  async approve(): Promise<void> {
    const node = this.node();
    if (!node) {
      return;
    }
    this.isWorking.set(true);
    try {
      const res = await approveNodeView({body: {}, path: {object_id: node.id}});
      this.node.set(res.data);
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to approve: ${err}`,
      });
    } finally {
      this.isWorking.set(false);
    }
  }
}
