from japanese.enums.node_type import NodeType


INGEST_PROMPT_KEY = 'japanese_ingest_v1'

INGEST_SYSTEM_PROMPT = (
    "You are a meticulous Japanese language teacher and parser. "
    "Given a Japanese input, you classify it (sentence, word, kanji, particle, or grammar rule), "
    "fill in structured fields for it, estimate its JLPT level, and extract every distinct sub-entity "
    "(contained words, kanji components, particles, and grammar rules used) for cross-linking. "
    "Always return dictionary forms for verbs/adjectives in base_form (e.g. 食べる, not 食べた)."
)

INGEST_USER_TEMPLATE = (
    "Analyze the following Japanese input and produce structured data plus every relevant sub-entity.\n\n"
    "Input:\n{text}\n\n"
    "Rules for canonical_key (used for dedup, must be deterministic):\n"
    "- sentence: the input Japanese text, trimmed, with internal whitespace normalised to single spaces.\n"
    "- word: '{{base_form}}|{{reading}}' (base_form in dictionary form, reading in hiragana).\n"
    "- kanji: the single kanji character.\n"
    "- particle: the particle itself (e.g. 'は').\n"
    "- rule: a short kebab-case slug (e.g. 'te-form', 'i-adjective-past').\n\n"
    "Rules for extracted_entities:\n"
    "- For a sentence input: list every word (dictionary form), every kanji that appears, every particle, "
    "and every grammar rule that the sentence demonstrates.\n"
    "- For a word input: list the kanji components and any rules used to derive its forms.\n"
    "- For a kanji/particle/rule input: list only entities truly required (often none).\n"
    "- Set surface_form to how the entity appears in the input (only meaningful for words used in a "
    "conjugated form inside a sentence; otherwise leave null).\n"
    "- edge_type_from_input: 'contains' for words/particles in a sentence; 'uses_rule' for rules used "
    "by a sentence/word; 'composed_of' for kanji components of a word; 'example_of' when a sentence is "
    "a clear textbook example of a rule.\n\n"
    "Only populate the one schema field matching node_type; leave the others null."
)


CONTENT_PROMPT_KEYS: dict[NodeType, str] = {
    NodeType.SENTENCE: 'japanese_content_sentence_v1',
    NodeType.WORD: 'japanese_content_word_v1',
    NodeType.KANJI: 'japanese_content_kanji_v1',
    NodeType.PARTICLE: 'japanese_content_particle_v1',
    NodeType.RULE: 'japanese_content_rule_v1',
}


_FURIGANA_RULE = (
    "Whenever you write a kanji word in Japanese text, immediately follow it with its reading in "
    "hiragana inside parentheses, e.g. 食(た)べる or 私(わたし). Do not use ruby tags."
)

_HTML_RULE = (
    "Return clean semantic HTML using only these tags: <h2>, <h3>, <p>, <ul>, <ol>, <li>, <strong>, "
    "<em>, <code>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <br>. Do not include <html>, <body>, "
    "or <style>. Do not add inline styles or class attributes."
)


CONTENT_SYSTEM_PROMPTS: dict[NodeType, str] = {
    NodeType.SENTENCE: (
        "You are a Japanese teacher writing study notes for an intermediate learner.\n"
        f"{_FURIGANA_RULE}\n{_HTML_RULE}"
    ),
    NodeType.WORD: (
        "You are a Japanese teacher writing a dictionary-style entry for an intermediate learner.\n"
        f"{_FURIGANA_RULE}\n{_HTML_RULE}"
    ),
    NodeType.KANJI: (
        "You are a Japanese teacher writing a kanji study card with a memorable mnemonic.\n"
        f"{_FURIGANA_RULE}\n{_HTML_RULE}"
    ),
    NodeType.PARTICLE: (
        "You are a Japanese teacher explaining a particle with clear contrasts and examples.\n"
        f"{_FURIGANA_RULE}\n{_HTML_RULE}"
    ),
    NodeType.RULE: (
        "You are a Japanese teacher explaining a grammar rule clearly, with patterns and examples.\n"
        f"{_FURIGANA_RULE}\n{_HTML_RULE}"
    ),
}


CONTENT_USER_TEMPLATES: dict[NodeType, str] = {
    NodeType.SENTENCE: (
        "Write study notes for this sentence.\n\n"
        "Japanese: {japanese}\n"
        "Translation: {english_translation}\n\n"
        "Sections to include:\n"
        "1. <h2>Meaning</h2> — natural translation plus literal breakdown.\n"
        "2. <h2>Structure</h2> — explain the grammatical structure piece by piece.\n"
        "3. <h2>Notes</h2> — any nuance, register, or cultural notes.\n"
        "Do NOT explain individual words in depth — those live in word nodes."
    ),
    NodeType.WORD: (
        "Write a dictionary-style entry for this word.\n\n"
        "Base form: {base_form}\n"
        "Reading: {reading}\n"
        "Word type: {word_type}\n"
        "Sub-type: {word_sub_type}\n"
        "Meanings: {meanings}\n\n"
        "Sections to include:\n"
        "1. <h2>Meaning</h2> — short definition and any nuance.\n"
        "2. <h2>Usage</h2> — typical contexts, register, common collocations.\n"
        "3. If verb or adjective: <h2>Conjugation</h2> — a compact <table> of the main forms "
        "(plain present/past/negative, polite present/past/negative, te-form).\n"
    ),
    NodeType.KANJI: (
        "Write a study card for this kanji.\n\n"
        "Character: {character}\n"
        "On readings: {readings_on}\n"
        "Kun readings: {readings_kun}\n"
        "Meanings: {meanings}\n"
        "Radicals: {radicals}\n\n"
        "Sections to include:\n"
        "1. <h2>Meaning</h2> — core meaning(s).\n"
        "2. <h2>Mnemonic</h2> — a vivid memorable image tying the radicals to the meaning.\n"
        "3. <h2>Common compounds</h2> — 3-6 common words using this kanji, each with reading and gloss."
    ),
    NodeType.PARTICLE: (
        "Write a study note for this particle.\n\n"
        "Particle: {particle}\n"
        "Primary function: {primary_function}\n\n"
        "Sections to include:\n"
        "1. <h2>Function</h2> — what it marks/does, with the typical pattern.\n"
        "2. <h2>Examples</h2> — 3-5 short example sentences with translation.\n"
        "3. <h2>Contrasts</h2> — common confusions with other particles, if any."
    ),
    NodeType.RULE: (
        "Write a study note for this grammar rule.\n\n"
        "Rule name: {name}\n"
        "Category: {category}\n\n"
        "Sections to include:\n"
        "1. <h2>Pattern</h2> — the formula/pattern, in <code>.\n"
        "2. <h2>Explanation</h2> — how it works, when to use it.\n"
        "3. <h2>Examples</h2> — 3-5 example sentences with translation.\n"
        "4. <h2>Exceptions</h2> — if any, otherwise omit this section."
    ),
}
