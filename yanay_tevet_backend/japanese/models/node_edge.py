from typing import TYPE_CHECKING

from django.db import models

from japanese.enums.edge_type import EdgeType
from japanese.models.node import Node


class NodeEdge(models.Model):
    if TYPE_CHECKING:
        id: int

    list_display = ['id', 'from_node', 'edge_type', 'to_node']
    list_filter = ['edge_type']

    from_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='outgoing_edges',
    )
    to_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='incoming_edges',
    )
    edge_type: EdgeType = models.CharField(
        max_length=32,
        choices=EdgeType.choices(),
    )
    edge_metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['from_node', 'to_node', 'edge_type'],
                name='japanese_nodeedge_unique_edge',
            ),
        ]
        indexes = [
            models.Index(fields=['from_node', 'edge_type']),
            models.Index(fields=['to_node', 'edge_type']),
        ]

    def __str__(self) -> str:
        return f'{self.from_node_id} -[{self.edge_type}]-> {self.to_node_id}'
