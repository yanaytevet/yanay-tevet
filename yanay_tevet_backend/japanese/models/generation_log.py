from typing import TYPE_CHECKING

from django.db import models

from japanese.models.node import Node


class GenerationLog(models.Model):
    if TYPE_CHECKING:
        id: int

    list_display = ['id', 'node', 'prompt_key', 'model_used', 'generated_at']
    list_filter = ['prompt_key', 'model_used']

    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='generation_logs',
    )
    prompt_key = models.CharField(max_length=128)
    model_used = models.CharField(max_length=128)
    input_payload = models.TextField()
    raw_output = models.TextField()

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['node', '-generated_at']),
        ]

    def __str__(self) -> str:
        return f'GenerationLog({self.id}) {self.prompt_key} -> node {self.node_id}'
