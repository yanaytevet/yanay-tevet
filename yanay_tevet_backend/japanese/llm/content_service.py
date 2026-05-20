import json

from common.generative_ai.enums.generative_ai_model import GenerativeAiModel
from common.generative_ai.text_generative_ai import TextGenerativeAI
from japanese.enums.node_status import NodeStatus
from japanese.enums.node_type import NodeType
from japanese.llm.prompts import (
    CONTENT_PROMPT_KEYS,
    CONTENT_SYSTEM_PROMPTS,
    CONTENT_USER_TEMPLATES,
)
from japanese.llm.schemas import ContentGenerationResult, ExtractedEntity
from japanese.models.generation_log import GenerationLog
from japanese.models.node import Node
from japanese.models.node_edge import NodeEdge


CONTENT_MODEL = GenerativeAiModel.GPT_4O


class ContentGenerationService:
    """Generates content_html for a node, fills its full schema, and creates
    stubs + edges for every referenced sub-entity.

    This is the heavy step. Ingest produces only a minimal stub; everything
    else is filled here.
    """

    @classmethod
    async def generate_for_node(cls, node: Node) -> Node:
        node_type = NodeType(node.type)
        user_prompt = cls._build_user_prompt(node, node_type)
        system_prompt = CONTENT_SYSTEM_PROMPTS[node_type]

        node.status = NodeStatus.GENERATING
        await node.asave()

        result = await TextGenerativeAI.generate_schema(
            prompt=user_prompt,
            schema_cls=ContentGenerationResult,
            model_type=CONTENT_MODEL,
            system_prompt=system_prompt,
        )

        cls._apply_full_schema(node, node_type, result)
        node.content_html = result.content_html
        node.status = NodeStatus.NEEDS_REVIEW
        await node.asave()

        for entity in result.extracted_entities:
            sub_node = await cls._upsert_entity_stub(entity)
            if sub_node.id == node.id:
                continue
            await cls._upsert_edge(node, sub_node, entity)

        await GenerationLog.objects.acreate(
            node=node,
            prompt_key=CONTENT_PROMPT_KEYS[node_type],
            model_used=CONTENT_MODEL.value,
            input_payload=user_prompt,
            raw_output=json.dumps(result.model_dump()),
        )

        return node

    @classmethod
    def _apply_full_schema(
        cls, node: Node, node_type: NodeType, result: ContentGenerationResult
    ) -> None:
        match node_type:
            case NodeType.SENTENCE:
                if result.sentence_data is not None:
                    node.sentence_data = result.sentence_data
            case NodeType.WORD:
                if result.word_data is not None:
                    node.word_data = result.word_data
            case NodeType.KANJI:
                if result.kanji_data is not None:
                    node.kanji_data = result.kanji_data
            case NodeType.PARTICLE:
                if result.particle_data is not None:
                    node.particle_data = result.particle_data
            case NodeType.RULE:
                if result.rule_data is not None:
                    node.rule_data = result.rule_data

    @classmethod
    async def _upsert_entity_stub(cls, entity: ExtractedEntity) -> Node:
        node_type = NodeType(entity.node_type)
        existing = await Node.objects.filter(
            type=node_type,
            canonical_key=entity.canonical_key,
        ).afirst()
        if existing is not None:
            if existing.jlpt_level is None and entity.jlpt_level is not None:
                existing.jlpt_level = entity.jlpt_level
                await existing.asave()
            return existing

        return await Node.objects.acreate(
            type=node_type,
            canonical_key=entity.canonical_key,
            jlpt_level=entity.jlpt_level,
            status=NodeStatus.STUB,
            sentence_data=entity.sentence_data,
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
    def _build_user_prompt(cls, node: Node, node_type: NodeType) -> str:
        template = CONTENT_USER_TEMPLATES[node_type]
        match node_type:
            case NodeType.SENTENCE:
                data = node.sentence_data
                if data is None:
                    raise ValueError(f'Node {node.id} of type sentence has no sentence_data')
                return template.format(
                    japanese=data.japanese,
                    english_translation=data.english_translation,
                )
            case NodeType.WORD:
                data = node.word_data
                if data is None:
                    raise ValueError(f'Node {node.id} of type word has no word_data')
                return template.format(
                    base_form=data.base_form,
                    reading=data.reading,
                    word_type=data.word_type,
                )
            case NodeType.KANJI:
                data = node.kanji_data
                if data is None:
                    raise ValueError(f'Node {node.id} of type kanji has no kanji_data')
                return template.format(character=data.character)
            case NodeType.PARTICLE:
                data = node.particle_data
                if data is None:
                    raise ValueError(f'Node {node.id} of type particle has no particle_data')
                return template.format(particle=data.particle)
            case NodeType.RULE:
                data = node.rule_data
                if data is None:
                    raise ValueError(f'Node {node.id} of type rule has no rule_data')
                return template.format(name=data.name)
