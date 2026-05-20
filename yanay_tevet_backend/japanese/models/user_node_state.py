from typing import TYPE_CHECKING

from django.db import models

from japanese.enums.user_node_status import UserNodeStatus
from japanese.models.node import Node
from users.models.user import User


class UserNodeState(models.Model):
    if TYPE_CHECKING:
        id: int

    list_display = ['id', 'user', 'node', 'status', 'next_review']
    list_filter = ['status']

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='japanese_node_states',
    )
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='user_states',
    )
    status: UserNodeStatus = models.CharField(
        max_length=32,
        choices=UserNodeStatus.choices(),
        default=UserNodeStatus.LEARNING,
        blank=True,
    )
    last_seen = models.DateTimeField(null=True, blank=True, default=None)
    next_review = models.DateTimeField(null=True, blank=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'node'],
                name='japanese_usernodestate_unique_user_node',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['next_review']),
        ]

    def __str__(self) -> str:
        return f'UserNodeState(user={self.user_id}, node={self.node_id}, {self.status})'
