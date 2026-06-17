export enum EdgeTypeEnum {
  CONTAINS = 'contains',
  COMPOSED_OF = 'composed_of',
  USES_RULE = 'uses_rule',
  EXAMPLE_OF = 'example_of',
  EXCEPTION_TO = 'exception_to',
  SYNONYM_OF = 'synonym_of',
  RELATED_TO = 'related_to',
  SAME_KANJI_AS = 'same_kanji_as',
}

export enum JlptLevelEnum {
  N5 = 'n5',
  N4 = 'n4',
  N3 = 'n3',
  N2 = 'n2',
  N1 = 'n1',
}

export enum NodeStatusEnum {
  STUB = 'stub',
  GENERATING = 'generating',
  NEEDS_REVIEW = 'needs_review',
  PUBLISHED = 'published',
}

export enum NodeTypeEnum {
  PASSAGE = 'passage',
  SENTENCE = 'sentence',
  WORD = 'word',
  KANJI = 'kanji',
  PARTICLE = 'particle',
  RULE = 'rule',
}

export enum RuleCategoryEnum {
  CONJUGATION = 'conjugation',
  SENTENCE_STRUCTURE = 'sentence_structure',
  POLITENESS = 'politeness',
  PARTICLE_USAGE = 'particle_usage',
  COUNTERS = 'counters',
  EXPRESSION_PATTERN = 'expression_pattern',
  OTHER = 'other',
}

export enum WordSubTypeEnum {
  GODAN = 'godan',
  ICHIDAN = 'ichidan',
  IRREGULAR_VERB = 'irregular_verb',
  I_ADJECTIVE = 'i_adjective',
  NA_ADJECTIVE = 'na_adjective',
}

export enum WordTypeEnum {
  VERB = 'verb',
  NOUN = 'noun',
  ADJECTIVE = 'adjective',
  ADVERB = 'adverb',
  EXPRESSION = 'expression',
  COUNTER = 'counter',
  PRONOUN = 'pronoun',
  INTERJECTION = 'interjection',
  CONJUNCTION = 'conjunction',
}
