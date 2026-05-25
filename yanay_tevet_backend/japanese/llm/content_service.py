import json

from common.generative_ai.enums.generative_ai_model import GenerativeAiModel
from common.generative_ai.text_generative_ai import TextGenerativeAI
from japanese.enums.edge_type import EdgeType
from japanese.enums.node_status import NodeStatus
from japanese.enums.node_type import NodeType
from japanese.llm.node_data_apply import apply_data_to_node
from japanese.llm.prompts import (
    CONTENT_PROMPT_KEYS,
    CONTENT_SYSTEM_PROMPTS,
    CONTENT_USER_TEMPLATES,
)
from japanese.llm.schemas import (
    ContentGenerationResult,
    ExtractedEntity,
    KanjiData,
    NodeData,
    ParticleData,
    WordData,
)
from japanese.models.generation_log import GenerationLog
from japanese.models.node import Node
from japanese.models.node_edge import NodeEdge
from japanese.models.user_node_state import UserNodeState


MAX_RELATED_SENTENCES_FOR_RULE = 5


CONTENT_MODEL = GenerativeAiModel.GPT_4O


class ContentGenerationService:
    """Generates content_html for a node, fills its full schema, and creates
    stubs + edges for every referenced sub-entity.

    This is the heavy step. Ingest produces only a minimal stub; everything
    else is filled here.
    """

    @classmethod
    async def generate_for_node(cls, node: Node, user_note: str | None = None) -> Node:
        node_type = NodeType(node.type)
        base_prompt = await cls._build_user_prompt(node, node_type)
        user_prompt = cls._prepend_user_note(base_prompt, user_note)
        system_prompt = CONTENT_SYSTEM_PROMPTS[node_type]

        node.status = NodeStatus.GENERATING
        await node.asave()

        result = await TextGenerativeAI.generate_schema(
            prompt=user_prompt,
            schema_cls=ContentGenerationResult,
            model_type=CONTENT_MODEL,
            system_prompt=system_prompt,
        )

        if NodeType(result.data.node_type) != node_type:
            raise ValueError(
                f'Content gen for node {node.id} ({node_type}) returned data '
                f'with mismatched node_type={result.data.node_type}'
            )

        # Decide where the new content lands: this node (renamed if needed) or an
        # existing canonical node it should merge into.
        surviving = await cls._resolve_surviving_node(node, node_type, result.data)

        apply_data_to_node(surviving, result.data)
        surviving.content_html = result.content_html
        surviving.status = NodeStatus.PUBLISHED
        await surviving.asave()

        await cls.clear_node_edges(surviving)

        if surviving.id != node.id:
            # Merging: hand over the source's incoming edges and user states, then delete it.
            await cls._absorb_into(source=node, target=surviving)

        for entity in result.extracted_entities:
            sub_node = await cls._upsert_entity_stub(entity)
            if sub_node.id == surviving.id:
                continue
            await cls._upsert_edge(surviving, sub_node, entity)

        await GenerationLog.objects.acreate(
            node=surviving,
            prompt_key=CONTENT_PROMPT_KEYS[node_type],
            model_used=CONTENT_MODEL.value,
            input_payload=user_prompt,
            raw_output=json.dumps(result.model_dump()),
        )

        return surviving

    @staticmethod
    def _prepend_user_note(prompt: str, user_note: str | None) -> str:
        if user_note is None:
            return prompt
        note = user_note.strip()
        if not note:
            return prompt
        return (
            'User-provided notes for this generation (the user submitted these instructions — '
            'follow them carefully and let them override default guidance when they conflict):\n'
            f'{note}\n\n'
        ) + prompt

    @classmethod
    async def _resolve_surviving_node(
        cls, node: Node, node_type: NodeType, data: NodeData,
    ) -> Node:
        """Pick which node should carry the new content.

        - If the generated data yields the same canonical_key, the original node survives.
        - If it yields a different key but no other node owns it, rename the original in place.
        - If another node already owns the new key, return that node — the original will be
          merged into it later (its incoming edges + user states get moved over, then it's deleted).

        Sentence and rule keys are not auto-derivable here, so those types always keep their
        original node.
        """
        new_key = cls._derive_canonical_key(node_type, data)
        if new_key is None or new_key == node.canonical_key:
            return node

        existing = await Node.objects.filter(
            type=node_type, canonical_key=new_key,
        ).exclude(id=node.id).afirst()
        if existing is not None:
            return existing

        node.canonical_key = new_key
        return node

    @staticmethod
    def _derive_canonical_key(node_type: NodeType, data: NodeData) -> str | None:
        match node_type:
            case NodeType.WORD:
                assert isinstance(data, WordData)
                return f'{data.base_form}|{data.reading}'
            case NodeType.KANJI:
                assert isinstance(data, KanjiData)
                return data.character
            case NodeType.PARTICLE:
                assert isinstance(data, ParticleData)
                return data.particle
            case NodeType.SENTENCE | NodeType.RULE:
                return None

    @classmethod
    async def _absorb_into(cls, source: Node, target: Node) -> None:
        """Hand source's incoming edges and user states over to target, then delete source.

        Source's outgoing edges are dropped (the regeneration already produced fresh ones on
        target). Source itself is deleted; cascade removes any remaining edges and states.
        """
        await NodeEdge.objects.filter(from_node_id=source.id).adelete()

        async for edge in source.incoming_edges.all():
            duplicate = await NodeEdge.objects.filter(
                from_node_id=edge.from_node_id,
                to_node_id=target.id,
                edge_type=edge.edge_type,
            ).afirst()
            if duplicate is None:
                edge.to_node_id = target.id
                await edge.asave()
            else:
                await edge.adelete()

        async for state in source.user_states.all():
            duplicate = await UserNodeState.objects.filter(
                user_id=state.user_id, node_id=target.id,
            ).afirst()
            if duplicate is None:
                state.node_id = target.id
                await state.asave()
            else:
                await state.adelete()

        await source.adelete()

    @classmethod
    async def _upsert_entity_stub(cls, entity: ExtractedEntity) -> Node:
        node_type = NodeType(entity.data.node_type)
        existing = await Node.objects.filter(
            type=node_type,
            canonical_key=entity.canonical_key,
        ).afirst()
        if existing is not None:
            dirty = False
            if existing.jlpt_level is None and entity.jlpt_level is not None:
                existing.jlpt_level = entity.jlpt_level
                dirty = True
            if _entity_data_should_replace(existing, node_type):
                apply_data_to_node(existing, entity.data)
                dirty = True
            if dirty:
                await existing.asave()
            return existing

        node = Node(
            type=node_type,
            canonical_key=entity.canonical_key,
            jlpt_level=entity.jlpt_level,
            status=NodeStatus.STUB,
        )
        apply_data_to_node(node, entity.data)
        await node.asave()
        return node

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
    async def _build_user_prompt(cls, node: Node, node_type: NodeType) -> str:
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
                related_sentences = await cls._fetch_related_sentences_for_rule(node)
                return template.format(name=data.name, related_sentences=related_sentences)

    @classmethod
    async def _fetch_related_sentences_for_rule(cls, rule_node: Node) -> str:
        edges_qs = NodeEdge.objects.filter(
            to_node=rule_node,
            edge_type__in=[EdgeType.USES_RULE, EdgeType.EXAMPLE_OF],
            from_node__type=NodeType.SENTENCE,
        ).select_related('from_node').order_by('-created_at')[:MAX_RELATED_SENTENCES_FOR_RULE]

        lines: list[str] = []
        async for edge in edges_qs:
            sentence_data = edge.from_node.sentence_data
            if sentence_data is None:
                continue
            lines.append(f'- {sentence_data.japanese} — {sentence_data.english_translation}')
        if not lines:
            return '(none yet — use your own judgment when writing the Examples section)'
        return '\n'.join(lines)

    @classmethod
    async def clear_node_edges(cls, node: Node) -> None:
        await NodeEdge.objects.filter(from_node=node).adelete()

def _entity_data_should_replace(existing: Node, node_type: NodeType) -> bool:
    """Stub-creation from extracted entities only carries minimum data; if the
    existing node already has any data of the matching type we keep it (it may
    have been enriched by an earlier content gen)."""
    match node_type:
        case NodeType.SENTENCE:
            return existing.sentence_data is None
        case NodeType.WORD:
            return existing.word_data is None
        case NodeType.KANJI:
            return existing.kanji_data is None
        case NodeType.PARTICLE:
            return existing.particle_data is None
        case NodeType.RULE:
            return existing.rule_data is None
