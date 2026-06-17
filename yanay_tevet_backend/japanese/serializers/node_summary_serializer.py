from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from japanese.enums.jlpt_level import JlptLevel
from japanese.enums.node_status import NodeStatus
from japanese.enums.node_type import NodeType
from japanese.models.node import Node
from japanese.schemas.kanji_schema import KanjiSchema
from japanese.schemas.particle_schema import ParticleSchema
from japanese.schemas.passage_schema import PassageSchema
from japanese.schemas.rule_schema import RuleSchema
from japanese.schemas.sentence_schema import SentenceSchema
from japanese.schemas.word_schema import WordSchema


class NodeSummarySchema(Schema):
    id: int
    type: NodeType
    status: NodeStatus
    canonical_key: str
    jlpt_level: JlptLevel | None

    passage_data: PassageSchema | None
    sentence_data: SentenceSchema | None
    word_data: WordSchema | None
    kanji_data: KanjiSchema | None
    particle_data: ParticleSchema | None
    rule_data: RuleSchema | None


class NodeSummarySerializer(Serializer[NodeSummarySchema]):
    async def inner_serialize(self, obj: Node) -> NodeSummarySchema:
        return NodeSummarySchema(
            id=obj.id,
            type=NodeType(obj.type),
            status=NodeStatus(obj.status),
            canonical_key=obj.canonical_key,
            jlpt_level=JlptLevel(obj.jlpt_level) if obj.jlpt_level else None,
            passage_data=obj.passage_data,
            sentence_data=obj.sentence_data,
            word_data=obj.word_data,
            kanji_data=obj.kanji_data,
            particle_data=obj.particle_data,
            rule_data=obj.rule_data,
        )
