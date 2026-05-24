import json

from common.generative_ai.enums.generative_ai_model import GenerativeAiModel
from common.generative_ai.text_generative_ai import TextGenerativeAI
from japanese.enums.node_status import NodeStatus
from japanese.enums.node_type import NodeType
from japanese.llm.content_service import ContentGenerationService
from japanese.llm.node_data_apply import apply_data_to_node, is_matching_data_missing
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
    """Classifies free Japanese text, creates the Node, and generates its content.

    Content generation is run inline for the ingested node only — sub-entities
    referenced by it are NOT stubbed or linked here. Those are created when
    ContentGenerationService runs explicitly on the node (or any other node
    that references them).
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

        await ContentGenerationService.generate_for_node(node)
        return node
