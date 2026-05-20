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
from japanese.llm.schemas import GeneratedContent
from japanese.models.generation_log import GenerationLog
from japanese.models.node import Node


CONTENT_MODEL = GenerativeAiModel.GPT_4_1


class ContentGenerationService:

    @classmethod
    async def generate_for_node(cls, node: Node) -> Node:
        node_type = NodeType(node.type)
        user_prompt = cls._build_user_prompt(node, node_type)
        system_prompt = CONTENT_SYSTEM_PROMPTS[node_type]

        node.status = NodeStatus.GENERATING
        await node.asave()

        result = await TextGenerativeAI.generate_schema(
            prompt=user_prompt,
            schema_cls=GeneratedContent,
            model_type=CONTENT_MODEL,
            system_prompt=system_prompt,
        )

        node.content_html = result.content_html
        node.status = NodeStatus.NEEDS_REVIEW
        await node.asave()

        await GenerationLog.objects.acreate(
            node=node,
            prompt_key=CONTENT_PROMPT_KEYS[node_type],
            model_used=CONTENT_MODEL.value,
            input_payload=user_prompt,
            raw_output=json.dumps(result.model_dump()),
        )

        return node

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
                    word_sub_type=data.word_sub_type or 'n/a',
                    meanings=', '.join(data.meanings),
                )
            case NodeType.KANJI:
                data = node.kanji_data
                if data is None:
                    raise ValueError(f'Node {node.id} of type kanji has no kanji_data')
                return template.format(
                    character=data.character,
                    readings_on=', '.join(data.readings_on) or 'n/a',
                    readings_kun=', '.join(data.readings_kun) or 'n/a',
                    meanings=', '.join(data.meanings),
                    radicals=', '.join(data.radicals) or 'n/a',
                )
            case NodeType.PARTICLE:
                data = node.particle_data
                if data is None:
                    raise ValueError(f'Node {node.id} of type particle has no particle_data')
                return template.format(
                    particle=data.particle,
                    primary_function=data.primary_function,
                )
            case NodeType.RULE:
                data = node.rule_data
                if data is None:
                    raise ValueError(f'Node {node.id} of type rule has no rule_data')
                return template.format(
                    name=data.name,
                    category=data.category,
                )
