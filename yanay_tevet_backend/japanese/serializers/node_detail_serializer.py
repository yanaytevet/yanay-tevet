from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from japanese.enums.edge_type import EdgeType
from japanese.models.node import Node
from japanese.serializers.node_summary_serializer import (
    NodeSummarySchema,
    NodeSummarySerializer,
)


class OutgoingEdgeSchema(Schema):
    id: int
    edge_type: EdgeType
    edge_metadata: dict
    to_node: NodeSummarySchema


class IncomingEdgeSchema(Schema):
    id: int
    edge_type: EdgeType
    edge_metadata: dict
    from_node: NodeSummarySchema


class NodeDetailSchema(NodeSummarySchema):
    content_html: str
    notes: str
    outgoing_edges: list[OutgoingEdgeSchema]
    incoming_edges: list[IncomingEdgeSchema]


class NodeDetailSerializer(Serializer[NodeDetailSchema]):
    async def inner_serialize(self, obj: Node) -> NodeDetailSchema:
        summary_serializer = NodeSummarySerializer()
        summary = await summary_serializer.inner_serialize(obj)

        outgoing: list[OutgoingEdgeSchema] = []
        async for edge in obj.outgoing_edges.select_related('to_node').all():
            to_summary = await summary_serializer.inner_serialize(edge.to_node)
            outgoing.append(OutgoingEdgeSchema(
                id=edge.id,
                edge_type=EdgeType(edge.edge_type),
                edge_metadata=edge.edge_metadata,
                to_node=to_summary,
            ))

        incoming: list[IncomingEdgeSchema] = []
        async for edge in obj.incoming_edges.select_related('from_node').all():
            from_summary = await summary_serializer.inner_serialize(edge.from_node)
            incoming.append(IncomingEdgeSchema(
                id=edge.id,
                edge_type=EdgeType(edge.edge_type),
                edge_metadata=edge.edge_metadata,
                from_node=from_summary,
            ))

        return NodeDetailSchema(
            **summary.model_dump(),
            content_html=obj.content_html,
            notes=obj.notes,
            outgoing_edges=outgoing,
            incoming_edges=incoming,
        )
