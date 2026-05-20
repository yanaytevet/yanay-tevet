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
from japanese.llm.schemas import IngestResult
from japanese.models.generation_log import GenerationLog
from japanese.models.node import Node


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

        node_type = NodeType(result.node_type)
        existing = await Node.objects.filter(
            type=node_type,
            canonical_key=result.canonical_key,
        ).afirst()

        if existing is None:
            node = await Node.objects.acreate(
                type=node_type,
                canonical_key=result.canonical_key,
                jlpt_level=result.jlpt_level,
                status=NodeStatus.STUB,
                sentence_data=result.sentence_data,
                word_data=result.word_data,
                kanji_data=result.kanji_data,
                particle_data=result.particle_data,
                rule_data=result.rule_data,
            )
        else:
            node = existing
            if node.jlpt_level is None and result.jlpt_level is not None:
                node.jlpt_level = result.jlpt_level
                await node.asave()

        await GenerationLog.objects.acreate(
            node=node,
            prompt_key=INGEST_PROMPT_KEY,
            model_used=INGEST_MODEL.value,
            input_payload=user_prompt,
            raw_output=json.dumps(result.model_dump()),
        )
        return node
