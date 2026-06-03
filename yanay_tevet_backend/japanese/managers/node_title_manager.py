from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from japanese.enums.node_type import NodeType
from japanese.models.node import Node


class NodeTitleManager:
    """Updates the primary display title of a node.

    The title maps to a different field per node type. For word/kanji/particle the
    canonical_key is deterministically derived from that field, so it is kept in sync
    (and uniqueness is enforced). Sentence and rule keys are not derivable, so their
    canonical_key is left untouched.
    """

    async def update_title(self, node: Node, title: str) -> None:
        title = title.strip()
        if not title:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                error_code='empty_title',
                message='Title cannot be empty.',
            )

        node_type = NodeType(node.type)
        match node_type:
            case NodeType.SENTENCE:
                if node.sentence_data is None:
                    raise self._missing_data(node_type)
                node.sentence_data = node.sentence_data.model_copy(update={'japanese': title})
            case NodeType.WORD:
                if node.word_data is None:
                    raise self._missing_data(node_type)
                node.word_data = node.word_data.model_copy(update={'base_form': title})
                await self._set_canonical_key(node, node_type, f'{title}|{node.word_data.reading}')
            case NodeType.KANJI:
                if node.kanji_data is None:
                    raise self._missing_data(node_type)
                node.kanji_data = node.kanji_data.model_copy(update={'character': title})
                await self._set_canonical_key(node, node_type, title)
            case NodeType.PARTICLE:
                if node.particle_data is None:
                    raise self._missing_data(node_type)
                node.particle_data = node.particle_data.model_copy(update={'particle': title})
                await self._set_canonical_key(node, node_type, title)
            case NodeType.RULE:
                if node.rule_data is None:
                    raise self._missing_data(node_type)
                node.rule_data = node.rule_data.model_copy(update={'name': title})

        await node.asave()

    async def _set_canonical_key(self, node: Node, node_type: NodeType, new_key: str) -> None:
        if new_key == node.canonical_key:
            return
        clash = await Node.objects.filter(
            type=node_type, canonical_key=new_key,
        ).exclude(id=node.id).aexists()
        if clash:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                error_code='duplicate_node',
                message=f'A {node_type.value} with this title already exists.',
            )
        node.canonical_key = new_key

    @staticmethod
    def _missing_data(node_type: NodeType) -> RestAPIException:
        return RestAPIException(
            status_code=StatusCode.HTTP_400_BAD_REQUEST,
            error_code='missing_node_data',
            message=f'This {node_type.value} node has no data to edit.',
        )
