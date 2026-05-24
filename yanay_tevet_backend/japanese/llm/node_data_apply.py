from japanese.enums.node_type import NodeType
from japanese.llm.schemas import (
    KanjiData,
    NodeData,
    ParticleData,
    RuleData,
    SentenceData,
    WordData,
)
from japanese.models.node import Node
from japanese.schemas.kanji_schema import KanjiSchema
from japanese.schemas.particle_schema import ParticleSchema
from japanese.schemas.rule_schema import RuleSchema
from japanese.schemas.sentence_schema import SentenceSchema
from japanese.schemas.word_schema import WordSchema


def apply_data_to_node(node: Node, data: NodeData) -> None:
    """Route a discriminated NodeData into the matching Node.*_data column.

    Strips the LLM discriminator field before persisting — the storage schema
    has no node_type field of its own.
    """
    payload = data.model_dump(exclude={'node_type'})
    match data:
        case SentenceData():
            node.sentence_data = SentenceSchema(**payload)
        case WordData():
            node.word_data = WordSchema(**payload)
        case KanjiData():
            node.kanji_data = KanjiSchema(**payload)
        case ParticleData():
            node.particle_data = ParticleSchema(**payload)
        case RuleData():
            node.rule_data = RuleSchema(**payload)


def is_matching_data_missing(node: Node, node_type: NodeType) -> bool:
    match node_type:
        case NodeType.SENTENCE:
            return node.sentence_data is None
        case NodeType.WORD:
            return node.word_data is None
        case NodeType.KANJI:
            return node.kanji_data is None
        case NodeType.PARTICLE:
            return node.particle_data is None
        case NodeType.RULE:
            return node.rule_data is None
