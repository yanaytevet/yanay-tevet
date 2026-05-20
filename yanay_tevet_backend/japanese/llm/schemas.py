from ninja import Schema

from japanese.enums.edge_type import EdgeType
from japanese.enums.jlpt_level import JlptLevel
from japanese.enums.node_type import NodeType
from japanese.schemas.kanji_schema import KanjiSchema
from japanese.schemas.particle_schema import ParticleSchema
from japanese.schemas.rule_schema import RuleSchema
from japanese.schemas.sentence_schema import SentenceSchema
from japanese.schemas.word_schema import WordSchema


class ExtractedEntity(Schema):
    """A sub-entity referenced by a node (word/kanji/particle/rule/sentence).

    Carries only the minimum identifying schema fields needed to create a stub —
    rich fields (meanings, conjugations, mnemonics, etc.) are filled lazily when
    that entity's own content is generated.

    Only the schema field matching `node_type` is populated; the rest are null.
    """
    node_type: NodeType
    canonical_key: str
    surface_form: str | None = None
    jlpt_level: JlptLevel | None = None
    edge_type_from_input: EdgeType

    sentence_data: SentenceSchema | None = None
    word_data: WordSchema | None = None
    kanji_data: KanjiSchema | None = None
    particle_data: ParticleSchema | None = None
    rule_data: RuleSchema | None = None


class IngestResult(Schema):
    """LLM output for ingesting a piece of Japanese text — minimum classification only.

    Populate the matching {type}_data field with ONLY the identifying fields
    (e.g. for a word: base_form, reading, word_type). Rich fields like meanings,
    conjugation hints, mnemonics, and readings lists are deferred to content gen.
    """
    node_type: NodeType
    canonical_key: str
    jlpt_level: JlptLevel | None = None

    sentence_data: SentenceSchema | None = None
    word_data: WordSchema | None = None
    kanji_data: KanjiSchema | None = None
    particle_data: ParticleSchema | None = None
    rule_data: RuleSchema | None = None


class ContentGenerationResult(Schema):
    """LLM output for generating a node's content + filling its full schema + linking entities.

    Populate the matching {type}_data field with the FULL schema (all meanings,
    conjugation hints, readings, mnemonics, etc.). Also produce content_html and
    the list of sub-entities to link.
    """
    content_html: str

    sentence_data: SentenceSchema | None = None
    word_data: WordSchema | None = None
    kanji_data: KanjiSchema | None = None
    particle_data: ParticleSchema | None = None
    rule_data: RuleSchema | None = None

    extracted_entities: list[ExtractedEntity]
