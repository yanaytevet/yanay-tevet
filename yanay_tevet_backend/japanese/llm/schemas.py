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
    """A sub-entity referenced by the input (word/kanji/particle/rule).

    Only the schema field matching `node_type` is populated; the rest are null.
    """
    node_type: NodeType
    canonical_key: str
    surface_form: str | None = None
    jlpt_level: JlptLevel | None = None
    edge_type_from_input: EdgeType

    word_data: WordSchema | None = None
    kanji_data: KanjiSchema | None = None
    particle_data: ParticleSchema | None = None
    rule_data: RuleSchema | None = None


class IngestResult(Schema):
    """LLM output for ingesting a piece of Japanese text.

    Only the schema field matching `node_type` is populated; the rest are null.
    """
    node_type: NodeType
    canonical_key: str
    jlpt_level: JlptLevel | None = None

    sentence_data: SentenceSchema | None = None
    word_data: WordSchema | None = None
    kanji_data: KanjiSchema | None = None
    particle_data: ParticleSchema | None = None
    rule_data: RuleSchema | None = None

    extracted_entities: list[ExtractedEntity]


class GeneratedContent(Schema):
    content_html: str
