from japanese.enums.node_type import NodeType


INGEST_PROMPT_KEY = 'japanese_ingest_v3'

INGEST_SYSTEM_PROMPT = (
    "You are a Japanese language classifier. Given a Japanese input, you identify its type "
    "(sentence, word, kanji, particle, or grammar rule) and produce ONLY the minimum identifying "
    "fields plus a deterministic canonical_key. Rich data (meanings, conjugations, mnemonics, "
    "function descriptions, JLPT readings) is filled later by a separate content step — do not "
    "produce it here."
)

INGEST_USER_TEMPLATE = (
    "Classify the following Japanese input and produce its minimum identifying data.\n\n"
    "Input:\n{text}\n\n"
    "Output shape:\n"
    "- canonical_key (deterministic, used for dedup) — rules below.\n"
    "- jlpt_level — provide if confident, else null.\n"
    "- data — pick the variant whose node_type matches the input and fill ONLY the minimum "
    "identifying fields. Exactly one variant is chosen; do not emit any other.\n\n"
    "canonical_key rules:\n"
    "- sentence: the input Japanese text, trimmed, internal whitespace collapsed to single spaces.\n"
    "- word: '{{base_form}}|{{reading}}' (base_form = dictionary form, reading = hiragana).\n"
    "- kanji: the single kanji character.\n"
    "- particle: the particle itself (e.g. 'は').\n"
    "- rule: a short kebab-case slug (e.g. 'te-form', 'i-adjective-past').\n\n"
    "data minimum fields by node_type:\n"
    "- sentence: japanese (with inline furigana as 漢字(かんじ)), english_translation.\n"
    "- word: base_form (dictionary form), reading (hiragana), word_type. "
    "Leave word_sub_type null and meanings empty.\n"
    "- kanji: character only. Leave readings_on, readings_kun, meanings, radicals empty.\n"
    "- particle: particle only. Leave primary_function empty.\n"
    "- rule: name only. Leave category at its default.\n\n"
    "Do NOT extract or list any related entities. That happens in the content step."
)


CONTENT_PROMPT_KEYS: dict[NodeType, str] = {
    NodeType.SENTENCE: 'japanese_content_sentence_v3',
    NodeType.WORD: 'japanese_content_word_v3',
    NodeType.KANJI: 'japanese_content_kanji_v3',
    NodeType.PARTICLE: 'japanese_content_particle_v3',
    NodeType.RULE: 'japanese_content_rule_v3',
}


_FURIGANA_RULE = (
    "Whenever you write a kanji word in Japanese text, immediately follow it with its reading in "
    "hiragana inside parentheses, e.g. 食(た)べる or 私(わたし). Do not use ruby tags."
)

_HTML_RULE = (
    "content_html must be clean semantic HTML using only these tags: <h2>, <h3>, <p>, <ul>, <ol>, "
    "<li>, <strong>, <em>, <code>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <br>. Do not "
    "include <html>, <body>, <style>, inline styles, or class attributes."
)

_OUTPUT_CONTRACT = (
    "Always produce three things in your structured output:\n"
    "1. content_html — the study notes (see Sections below).\n"
    "2. data — the variant whose node_type matches THIS node, with ALL fields populated (not just "
    "the identifying ones). The discriminator (data.node_type) MUST equal the node's type.\n"
    "3. extracted_entities — every distinct sub-entity that this node references.\n\n"
    "extracted_entities rules:\n"
    "- Each entity carries canonical_key, edge_type_from_input, optional surface_form/jlpt_level, "
    "and `data` — a variant whose node_type identifies the entity. Fill ONLY the MINIMUM "
    "identifying fields in data (same minimum rules as ingest: word → base_form/reading/word_type "
    "only; kanji → character only; particle → particle only; rule → name only). Do NOT include "
    "meanings, readings, mnemonics or function descriptions for sub-entities — those will be "
    "filled when their own content is generated.\n"
    "- canonical_key rules: same as ingest (word = base_form|reading, kanji = character, etc.).\n"
    "- surface_form: how the entity appears in this node (set for words used in a conjugated form "
    "inside a sentence; otherwise null).\n"
    "- edge_type_from_input: 'contains' for words/particles inside a sentence; 'composed_of' for "
    "kanji components of a word; 'uses_rule' for rules used by a sentence/word; 'example_of' when "
    "a sentence is a textbook example of a rule; 'exception_to' for exceptions to a rule.\n"
    "- Only emit outgoing references that are downward in the graph. Do NOT list sentences that "
    "use a kanji from a kanji node — those reverse links are created when each sentence's content "
    "is generated."
)


CONTENT_SYSTEM_PROMPTS: dict[NodeType, str] = {
    NodeType.SENTENCE: (
        "You are a Japanese teacher writing study notes for an intermediate learner.\n"
        f"{_FURIGANA_RULE}\n{_HTML_RULE}\n{_OUTPUT_CONTRACT}"
    ),
    NodeType.WORD: (
        "You are a Japanese teacher writing a dictionary-style entry for an intermediate learner.\n"
        f"{_FURIGANA_RULE}\n{_HTML_RULE}\n{_OUTPUT_CONTRACT}"
    ),
    NodeType.KANJI: (
        "You are a Japanese teacher writing a kanji study card with a memorable mnemonic.\n"
        f"{_FURIGANA_RULE}\n{_HTML_RULE}\n{_OUTPUT_CONTRACT}"
    ),
    NodeType.PARTICLE: (
        "You are a Japanese teacher explaining a particle with clear contrasts and examples.\n"
        f"{_FURIGANA_RULE}\n{_HTML_RULE}\n{_OUTPUT_CONTRACT}"
    ),
    NodeType.RULE: (
        "You are a Japanese teacher explaining a grammar rule clearly, with patterns and examples.\n"
        f"{_FURIGANA_RULE}\n{_HTML_RULE}\n{_OUTPUT_CONTRACT}"
    ),
}


CONTENT_USER_TEMPLATES: dict[NodeType, str] = {
    NodeType.SENTENCE: (
        "Generate full content + linked entities for this sentence node.\n\n"
        "Japanese: {japanese}\n"
        "Translation: {english_translation}\n\n"
        "content_html sections:\n"
        "1. <h2>Meaning</h2> — natural translation plus literal breakdown.\n"
        "2. <h2>Structure</h2> — explain the grammatical structure piece by piece.\n"
        "3. <h2>Notes</h2> — any nuance, register, or cultural notes.\n"
        "Do NOT explain individual words in depth — those live in word nodes.\n\n"
        "data: pick node_type=sentence and re-emit japanese + english_translation (with furigana "
        "on the japanese).\n\n"
        "extracted_entities: every distinct word (dictionary form), every kanji that appears in any "
        "of those words, every particle used, and every grammar rule the sentence demonstrates."
    ),
    NodeType.WORD: (
        "Generate full content + linked entities for this word node.\n\n"
        "Base form: {base_form}\n"
        "Reading: {reading}\n"
        "Word type: {word_type}\n\n"
        "content_html sections:\n"
        "1. <h2>Meaning</h2> — short definition and any nuance.\n"
        "2. <h2>Usage</h2> — typical contexts, register, common collocations.\n"
        "3. If verb or adjective: <h2>Conjugation</h2> — a compact <table> of the main forms "
        "(plain present/past/negative, polite present/past/negative, te-form).\n\n"
        "data: pick node_type=word and re-emit base_form, reading, word_type, plus the full "
        "word_sub_type (for verbs: godan/ichidan/irregular_verb; for adjectives: i_adjective/"
        "na_adjective; else null) and meanings (an ordered list of English glosses).\n\n"
        "extracted_entities: every kanji that appears in the base_form, and any grammar rule(s) "
        "the word's conjugation depends on (e.g. for 食べる: rule 'ichidan-conjugation')."
    ),
    NodeType.KANJI: (
        "Generate full content + linked entities for this kanji node.\n\n"
        "Character: {character}\n\n"
        "content_html sections:\n"
        "1. <h2>Meaning</h2> — core meaning(s).\n"
        "2. <h2>Mnemonic</h2> — a vivid memorable image tying the radicals to the meaning.\n"
        "3. <h2>Common compounds</h2> — 3-6 common words using this kanji, each with reading and "
        "gloss.\n\n"
        "data: pick node_type=kanji and re-emit character, plus full readings_on, readings_kun, "
        "meanings, radicals.\n\n"
        "extracted_entities: leave empty. Reverse links from words and sentences are created "
        "automatically when those nodes' content is generated."
    ),
    NodeType.PARTICLE: (
        "Generate full content + linked entities for this particle node.\n\n"
        "Particle: {particle}\n\n"
        "content_html sections:\n"
        "1. <h2>Function</h2> — what it marks/does, with the typical pattern.\n"
        "2. <h2>Examples</h2> — 3-5 short example sentences with translation.\n"
        "3. <h2>Contrasts</h2> — common confusions with other particles, if any.\n\n"
        "data: pick node_type=particle and re-emit particle, plus a concise primary_function "
        "(one short sentence).\n\n"
        "extracted_entities: leave empty."
    ),
    NodeType.RULE: (
        "Generate full content + linked entities for this grammar rule node.\n\n"
        "Rule name: {name}\n\n"
        "content_html sections:\n"
        "1. <h2>Pattern</h2> — the formula/pattern, in <code>.\n"
        "2. <h2>Explanation</h2> — how it works, when to use it.\n"
        "3. <h2>Examples</h2> — 3-5 example sentences with translation.\n"
        "4. <h2>Exceptions</h2> — if any, otherwise omit this section.\n\n"
        "data: pick node_type=rule and re-emit name plus the proper category (conjugation, "
        "sentence_structure, politeness, particle_usage, counters, expression_pattern, or other).\n\n"
        "extracted_entities: leave empty."
    ),
}
