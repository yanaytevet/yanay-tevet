from typing import Literal

from ninja import Schema

from japanese.enums.edge_type import EdgeType
from japanese.enums.jlpt_level import JlptLevel
from japanese.enums.node_type import NodeType
from japanese.schemas.kanji_schema import KanjiSchema
from japanese.schemas.particle_schema import ParticleSchema
from japanese.schemas.rule_schema import RuleSchema
from japanese.schemas.sentence_schema import SentenceSchema
from japanese.schemas.word_schema import WordSchema


class SentenceData(SentenceSchema):
    node_type: Literal[NodeType.SENTENCE] = NodeType.SENTENCE


class WordData(WordSchema):
    node_type: Literal[NodeType.WORD] = NodeType.WORD


class KanjiData(KanjiSchema):
    node_type: Literal[NodeType.KANJI] = NodeType.KANJI


class ParticleData(ParticleSchema):
    node_type: Literal[NodeType.PARTICLE] = NodeType.PARTICLE


class RuleData(RuleSchema):
    node_type: Literal[NodeType.RULE] = NodeType.RULE


# Plain Union (no pydantic discriminator) so the JSON schema emits `anyOf`
# instead of `oneOf` — OpenAI's structured outputs reject `oneOf`. The Literal
# `node_type` on each variant still gives Pydantic enough info to parse
# responses into the correct subtype.
NodeData = SentenceData | WordData | KanjiData | ParticleData | RuleData


class ExtractedEntity(Schema):
    """A sub-entity referenced by a node (word/kanji/particle/rule/sentence).

    The `data` field is a discriminated union: its `node_type` selects the
    matching schema and forces exactly one shape to be filled. Sub-entities
    carry only the minimum identifying fields; rich fields are lazy-filled
    when the entity's own content is generated.
    """
    canonical_key: str
    surface_form: str | None = None
    jlpt_level: JlptLevel | None = None
    edge_type_from_input: EdgeType
    data: NodeData


class IngestResult(Schema):
    """LLM output for ingesting a piece of Japanese text — minimum classification only.

    The `data` field is a discriminated union on `node_type`. The LLM picks
    one shape (sentence/word/kanji/particle/rule) and fills only the
    identifying fields — rich fields are deferred to content gen.
    """
    canonical_key: str
    jlpt_level: JlptLevel | None = None
    data: NodeData


class ContentGenerationResult(Schema):
    """LLM output for generating a node's content + filling its full schema + linking entities.

    The `data` field is a discriminated union and must match the node being
    generated for. All fields of the chosen schema are populated (not just the
    identifying ones).
    """
    content_html: str
    data: NodeData
    extracted_entities: list[ExtractedEntity]
