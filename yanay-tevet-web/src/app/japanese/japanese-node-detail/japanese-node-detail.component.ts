import {Component, computed, inject, signal} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {DomSanitizer, SafeHtml} from '@angular/platform-browser';
import {
  approveNodeView,
  generateContentView,
  readNodeView,
  NodeDetailSchema,
  EdgeType,
  IncomingEdgeSchema,
  OutgoingEdgeSchema,
} from '../../../generated-files/api/japanese';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {FuriganaComponent} from '../shared/furigana/furigana.component';
import {JapaneseNavComponent} from '../shared/japanese-nav/japanese-nav.component';
import {NodeSummaryCardComponent} from '../shared/node-summary-card/node-summary-card.component';

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
  imports: [FuriganaComponent, JapaneseNavComponent, NodeSummaryCardComponent],
  templateUrl: './japanese-node-detail.component.html',
})
export class JapaneseNodeDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly sanitizer = inject(DomSanitizer);
  private readonly dialogService = inject(DialogService);
  protected readonly authService = inject(AuthenticationService);

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
    this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        void this.load(Number(idStr));
      }
    });
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

  async generate(): Promise<void> {
    const node = this.node();
    if (!node) {
      return;
    }
    this.isWorking.set(true);
    try {
      const res = await generateContentView({body: {}, path: {object_id: node.id}});
      this.node.set(res.data);
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to generate content: ${err}`,
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
