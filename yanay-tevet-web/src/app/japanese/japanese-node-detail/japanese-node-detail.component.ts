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
import {fill, injectStrings} from '../../shared/i18n/strings';
import {JAPANESE_STRINGS} from '../i18n';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {ErrorStateComponent} from '../../common/components/page/error-state/error-state.component';
import {FuriganaComponent} from '../shared/furigana/furigana.component';
import {JapaneseNavComponent} from '../shared/japanese-nav/japanese-nav.component';
import {EMPTY_NODE_DISPLAY, nodeDisplay, NodeDisplay} from '../shared/node-display';
import {NodeSummaryCardComponent} from '../shared/node-summary-card/node-summary-card.component';
import {SpeakButtonComponent} from '../shared/speak-button/speak-button.component';

@Component({
  selector: 'app-japanese-node-detail',
  standalone: true,
  imports: [
    FuriganaComponent, JapaneseNavComponent, NodeSummaryCardComponent, SpeakButtonComponent,
    PageHeaderComponent, LoadingStateComponent, ErrorStateComponent,
  ],
  templateUrl: './japanese-node-detail.component.html',
})
export class JapaneseNodeDetailComponent extends BasePageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly sanitizer = inject(DomSanitizer);
  private readonly dialogService = inject(DialogService);
  private readonly routingService = inject(RoutingService);
  private readonly userWebsocketsService = inject(UserWebsocketsService);
  protected readonly authService = inject(AuthenticationService);
  protected readonly t = injectStrings(JAPANESE_STRINGS);

  private currentNodeId: number | null = null;
  private nodeWsSubscription: Subscription | null = null;

  readonly node = signal<NodeDetailSchema | null>(null);
  readonly isLoading = signal<boolean>(true);
  readonly isWorking = signal<boolean>(false);
  readonly notFound = signal<boolean>(false);

  readonly japaneseHomeUrl = this.routingService.getJapaneseHomeUrl();

  readonly display = computed<NodeDisplay>(() => {
    const node = this.node();
    return node ? nodeDisplay(node, this.t()) : EMPTY_NODE_DISPLAY;
  });

  readonly radicalsLabel = computed(() => fill(this.t().detail.radicals, {radicals: this.display().radicals}));

  readonly nodeTitle = computed<string>(() => {
    const node = this.node();
    if (!node) {
      return '';
    }
    return (
      node.passage_data?.title ??
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
      label: this.t().detail.outgoing[type],
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
      label: this.t().detail.incoming[type],
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
    this.notFound.set(false);
    try {
      const res = await readNodeView({path: {object_id: id}});
      this.node.set(res.data);
    } catch {
      this.notFound.set(true);
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

    const strings = this.t().detail;
    const userNote = await this.dialogService.getTextFromInputDialog({
      title: strings.generateContent,
      text: strings.generateDialog.text,
      label: strings.generateDialog.label,
      isTextArea: true,
      textAreaRows: 5,
      allowEmpty: true,
      confirmActionName: strings.generateDialog.confirm,
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
        title: this.t().detail.error,
        text: fill(this.t().detail.generateFailed, {error: String(err)}),
      });
    }
  }

  async editTitle(): Promise<void> {
    const node = this.node();
    if (!node) {
      return;
    }
    const strings = this.t().detail;
    const title = await this.dialogService.getTextFromInputDialog({
      title: strings.editTitle,
      text: strings.editTitleDialog.text,
      label: strings.editTitleDialog.label,
      defaultValue: this.nodeTitle(),
      confirmActionName: strings.editTitleDialog.confirm,
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
        title: this.t().detail.error,
        text: fill(this.t().detail.updateTitleFailed, {error: String(err)}),
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
        title: this.t().detail.error,
        text: fill(this.t().detail.approveFailed, {error: String(err)}),
      });
    } finally {
      this.isWorking.set(false);
    }
  }
}
