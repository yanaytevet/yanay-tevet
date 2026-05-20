import json

from common.generative_ai.enums.generative_ai_model import GenerativeAiModel
from common.generative_ai.text_generative_ai import TextGenerativeAI
from japanese.enums.node_status import NodeStatus
from japanese.enums.node_type import NodeType
from japanese.llm.content_service import ContentGenerationService
from japanese.llm.prompts import (
    INGEST_PROMPT_KEY,
    INGEST_SYSTEM_PROMPT,
    INGEST_USER_TEMPLATE,
)
from japanese.llm.schemas import ExtractedEntity, IngestResult
from japanese.models.generation_log import GenerationLog
from japanese.models.node import Node
from japanese.models.node_edge import NodeEdge


INGEST_MODEL = GenerativeAiModel.GPT_4_1


class IngestService:

    @classmethod
    async def ingest(cls, text: str) -> Node:
        user_prompt = INGEST_USER_TEMPLATE.format(text=text)
        result = await TextGenerativeAI.generate_schema(
            prompt=user_prompt,
            schema_cls=IngestResult,
            model_type=INGEST_MODEL,
            system_prompt=INGEST_SYSTEM_PROMPT,
        )

        main_node = await cls._upsert_main_node(
            result,
            input_payload=user_prompt,
            raw_output=json.dumps(result.model_dump()),
        )

        for entity in result.extracted_entities:
            sub_node = await cls._upsert_entity_stub(entity)
            if sub_node.id == main_node.id:
                continue
            await cls._upsert_edge(main_node, sub_node, entity)

        await ContentGenerationService.generate_for_node(main_node)
        return main_node

    @classmethod
    async def _upsert_main_node(cls, result: IngestResult, input_payload: str, raw_output: str) -> Node:
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
            cls._fill_missing_schema(node, result)
            if node.jlpt_level is None and result.jlpt_level is not None:
                node.jlpt_level = result.jlpt_level
            await node.asave()

        await GenerationLog.objects.acreate(
            node=node,
            prompt_key=INGEST_PROMPT_KEY,
            model_used=INGEST_MODEL.value,
            input_payload=input_payload,
            raw_output=raw_output,
        )
        return node

    @classmethod
    async def _upsert_entity_stub(cls, entity: ExtractedEntity) -> Node:
        node_type = NodeType(entity.node_type)
        existing = await Node.objects.filter(
            type=node_type,
            canonical_key=entity.canonical_key,
        ).afirst()
        if existing is not None:
            cls._fill_missing_entity_schema(existing, entity)
            if existing.jlpt_level is None and entity.jlpt_level is not None:
                existing.jlpt_level = entity.jlpt_level
            await existing.asave()
            return existing

        return await Node.objects.acreate(
            type=node_type,
            canonical_key=entity.canonical_key,
            jlpt_level=entity.jlpt_level,
            status=NodeStatus.STUB,
            word_data=entity.word_data,
            kanji_data=entity.kanji_data,
            particle_data=entity.particle_data,
            rule_data=entity.rule_data,
        )

    @classmethod
    async def _upsert_edge(cls, from_node: Node, to_node: Node, entity: ExtractedEntity) -> None:
        metadata: dict[str, str] = {}
        if entity.surface_form:
            metadata['surface_form'] = entity.surface_form

        existing = await NodeEdge.objects.filter(
            from_node=from_node,
            to_node=to_node,
            edge_type=entity.edge_type_from_input,
        ).afirst()
        if existing is not None:
            if metadata and existing.edge_metadata != metadata:
                existing.edge_metadata = metadata
                await existing.asave()
            return

        await NodeEdge.objects.acreate(
            from_node=from_node,
            to_node=to_node,
            edge_type=entity.edge_type_from_input,
            edge_metadata=metadata,
        )

    @classmethod
    def _fill_missing_schema(cls, node: Node, result: IngestResult) -> None:
        if node.sentence_data is None and result.sentence_data is not None:
            node.sentence_data = result.sentence_data
        if node.word_data is None and result.word_data is not None:
            node.word_data = result.word_data
        if node.kanji_data is None and result.kanji_data is not None:
            node.kanji_data = result.kanji_data
        if node.particle_data is None and result.particle_data is not None:
            node.particle_data = result.particle_data
        if node.rule_data is None and result.rule_data is not None:
            node.rule_data = result.rule_data

    @classmethod
    def _fill_missing_entity_schema(cls, node: Node, entity: ExtractedEntity) -> None:
        if node.word_data is None and entity.word_data is not None:
            node.word_data = entity.word_data
        if node.kanji_data is None and entity.kanji_data is not None:
            node.kanji_data = entity.kanji_data
        if node.particle_data is None and entity.particle_data is not None:
            node.particle_data = entity.particle_data
        if node.rule_data is None and entity.rule_data is not None:
            node.rule_data = entity.rule_data
