import type {EdgeType, NodeStatus, NodeType} from '../../../generated-files/api/japanese';

// The Japanese app's interface strings (the learning content itself comes from the backend and is shown as is).
// This file is the contract: every other language's file is typed against it. The admin-only ingest and review
// pages stay English and don't use it.
export const en = {
  title: 'Japanese',
  subtitle: 'Explore a network of passages, sentences, words, kanji, particles, and grammar rules.',
  nav: {
    explore: 'Explore',
    ingest: 'Ingest',
    review: 'Review',
  },
  // Tab titles on the explore page.
  tabs: {
    passage: 'Passages',
    sentence: 'Sentences',
    word: 'Words',
    kanji: 'Kanji',
    particle: 'Particles',
    rule: 'Rules',
  } satisfies Record<NodeType, string>,
  // A single node's type, on its card and page.
  nodeTypes: {
    passage: 'Passage',
    sentence: 'Sentence',
    word: 'Word',
    kanji: 'Kanji',
    particle: 'Particle',
    rule: 'Rule',
  } satisfies Record<NodeType, string>,
  statuses: {
    stub: 'Stub',
    generating: 'Generating',
    needs_review: 'Needs review',
    published: 'Published',
  } satisfies Record<NodeStatus, string>,

  explore: {
    shuffle: 'Shuffle',
    loadFailed: 'Couldn\'t load. Try again in a moment.',
    emptyText: 'Ingested text and the entities generated from it show up here.',
    emptyTitles: {
      passage: 'No passages yet',
      sentence: 'No sentences yet',
      word: 'No words yet',
      kanji: 'No kanji yet',
      particle: 'No particles yet',
      rule: 'No rules yet',
    } satisfies Record<NodeType, string>,
  },

  speak: {
    readAloud: 'Read aloud in Japanese',
    stop: 'Stop',
    loop: 'Loop',
    loopOn: 'Looping on',
  },

  detail: {
    loading: 'Loading',
    notFound: 'Node not found.',
    backToJapanese: 'Back to Japanese',
    radicals: 'Radicals: {radicals}',
    noContent: 'No content yet.',
    noContentAdmin: 'No content yet. Click “Generate content” to create it.',
    linksFrom: 'Links from this node',
    linksTo: 'Links to this node',
    // Groups of linked nodes, by how this node links to them.
    outgoing: {
      contains: 'Contains',
      composed_of: 'Composed of',
      uses_rule: 'Uses rule',
      example_of: 'Example of',
      exception_to: 'Exception to',
      synonym_of: 'Synonym of',
      related_to: 'Related',
      same_kanji_as: 'Same kanji as',
    } satisfies Record<EdgeType, string>,
    // … and by how they link to it.
    incoming: {
      contains: 'Appears in',
      composed_of: 'Used in words',
      uses_rule: 'Sentences using this rule',
      example_of: 'Examples',
      exception_to: 'Exceptions',
      synonym_of: 'Synonyms',
      related_to: 'Related',
      same_kanji_as: 'Same kanji as',
    } satisfies Record<EdgeType, string>,

    // Admin controls on the node page.
    editTitle: 'Edit title',
    generateContent: 'Generate content',
    approve: 'Approve',
    regenerate: 'Regenerate',
    generateDialog: {
      text: 'Optional notes to guide the model (e.g. “use the kanji form 中”, “treat this as a noun, not a verb”, “this is the polite copula”). Leave empty to generate with the default rules.',
      label: 'Notes (optional)',
      confirm: 'Generate',
    },
    editTitleDialog: {
      text: 'Update the main text shown for this node. For words and sentences you can include furigana like 漢字(かんじ).',
      label: 'Title',
      confirm: 'Save',
    },
    error: 'Error',
    generateFailed: 'Failed to generate content: {error}',
    updateTitleFailed: 'Failed to update the title: {error}',
    approveFailed: 'Failed to approve: {error}',
  },
};

export type JapaneseStrings = typeof en;
