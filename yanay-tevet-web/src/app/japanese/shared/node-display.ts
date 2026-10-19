import {NodeStatus, NodeSummarySchema} from '../../../generated-files/api/japanese';

const STATUS_CHIP_CLASS: Record<NodeStatus, string> = {
  published: 'chip-success',
  needs_review: 'chip-warning',
  generating: 'chip-info',
  stub: '',
};

export interface NodeDisplay {
  typeLabel: string;
  statusLabel: string;
  statusChipClass: string;
  jlptLabel: string;
  meanings: string;
  readingsOn: string;
  readingsKun: string;
  radicals: string;
}

export const EMPTY_NODE_DISPLAY: NodeDisplay = {
  typeLabel: '',
  statusLabel: '',
  statusChipClass: '',
  jlptLabel: '',
  meanings: '',
  readingsOn: '',
  readingsKun: '',
  radicals: '',
};

// The display strings a node card or page shows, computed once so templates only read fields.
export function nodeDisplay(
  node: Pick<NodeSummarySchema, 'type' | 'status' | 'jlpt_level' | 'word_data' | 'kanji_data'>,
): NodeDisplay {
  const meanings = node.word_data?.meanings ?? node.kanji_data?.meanings ?? [];
  return {
    typeLabel: node.type.charAt(0).toUpperCase() + node.type.slice(1),
    statusLabel: node.status.replace(/_/g, ' '),
    statusChipClass: STATUS_CHIP_CLASS[node.status],
    jlptLabel: node.jlpt_level?.toUpperCase() ?? '',
    meanings: meanings.join(', '),
    readingsOn: (node.kanji_data?.readings_on ?? []).join('、'),
    readingsKun: (node.kanji_data?.readings_kun ?? []).join('、'),
    radicals: (node.kanji_data?.radicals ?? []).join(' '),
  };
}
