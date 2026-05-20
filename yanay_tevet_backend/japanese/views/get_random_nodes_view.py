from typing import Type

from ninja import Query, Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from japanese.enums.node_status import NodeStatus
from japanese.enums.node_type import NodeType
from japanese.models.node import Node
from japanese.serializers.node_summary_serializer import (
    NodeSummarySchema,
    NodeSummarySerializer,
)


class GetRandomNodesQuery(Schema):
    types: str = 'sentence,rule'
    count: int = 6


class GetRandomNodesResponseSchema(Schema):
    nodes: list[NodeSummarySchema]


class GetRandomNodesView(SimpleGetAPIView):
    @classmethod
    async def check_permitted(cls, request: APIRequest, query: GetRandomNodesQuery = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(
        cls, request: APIRequest, query: GetRandomNodesQuery = None, path: Path = None
    ) -> GetRandomNodesResponseSchema:
        if query is None:
            query = GetRandomNodesQuery()
        requested_types = cls._parse_types(query.types)
        count = max(1, min(query.count, 50))

        qs = Node.objects.filter(
            type__in=requested_types,
            status=NodeStatus.PUBLISHED,
        ).order_by('?')[:count]

        serializer = NodeSummarySerializer()
        nodes = await serializer.serialize_query(qs)
        return GetRandomNodesResponseSchema(nodes=nodes)

    @classmethod
    def get_query_params_schema(cls) -> Type[Schema]:
        return GetRandomNodesQuery

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return GetRandomNodesResponseSchema

    @classmethod
    def _parse_types(cls, raw: str) -> list[NodeType]:
        if not raw.strip():
            return [NodeType.SENTENCE, NodeType.RULE]
        result: list[NodeType] = []
        for piece in raw.split(','):
            piece = piece.strip()
            if not piece:
                continue
            result.append(NodeType(piece))
        return result or [NodeType.SENTENCE, NodeType.RULE]
