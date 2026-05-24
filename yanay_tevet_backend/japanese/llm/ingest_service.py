import json

from common.generative_ai.enums.generative_ai_model import GenerativeAiModel
from common.generative_ai.text_generative_ai import TextGenerativeAI
from japanese.enums.node_status import NodeStatus
from japanese.enums.node_type import NodeType
from japanese.llm.prompts import (
    INGEST_PROMPT_KEY,
    INGEST_SYSTEM_PROMPT,
    INGEST_USER_TEMPLATE,
)
from japanese.llm.schemas import (
    IngestResult,
    KanjiData,
    NodeData,
    ParticleData,
    RuleData,
    SentenceData,
    WordData,
)
from japanese.models.generation_log import GenerationLog
from japanese.models.node import Node
from japanese.schemas.kanji_schema import KanjiSchema
from japanese.schemas.particle_schema import ParticleSchema
from japanese.schemas.rule_schema import RuleSchema
from japanese.schemas.sentence_schema import SentenceSchema
from japanese.schemas.word_schema import WordSchema


INGEST_MODEL = GenerativeAiModel.GPT_4O


class IngestService:
    """Classifies free Japanese text and creates the bare-minimum stub Node.

    No entity extraction, no edges, no content generation — that all happens
    later when ContentGenerationService runs on this (or any) node.
    """

    @classmethod
    async def ingest(cls, text: str) -> Node:
        user_prompt = INGEST_USER_TEMPLATE.format(text=text)
        result = await TextGenerativeAI.generate_schema(
            prompt=user_prompt,
            schema_cls=IngestResult,
            model_type=INGEST_MODEL,
            system_prompt=INGEST_SYSTEM_PROMPT,
        )

        node_type = NodeType(result.data.node_type)
        existing = await Node.objects.filter(
            type=node_type,
            canonical_key=result.canonical_key,
        ).afirst()

        if existing is None:
            node = Node(
                type=node_type,
                canonical_key=result.canonical_key,
                jlpt_level=result.jlpt_level,
                status=NodeStatus.STUB,
            )
            apply_data_to_node(node, result.data)
            await node.asave()
        else:
            node = existing
            dirty = False
            if node.jlpt_level is None and result.jlpt_level is not None:
                node.jlpt_level = result.jlpt_level
                dirty = True
            if is_matching_data_missing(node, node_type):
                apply_data_to_node(node, result.data)
                dirty = True
            if dirty:
                await node.asave()

        await GenerationLog.objects.acreate(
            node=node,
            prompt_key=INGEST_PROMPT_KEY,
            model_used=INGEST_MODEL.value,
            input_payload=user_prompt,
            raw_output=json.dumps(result.model_dump()),
        )
        return node


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
