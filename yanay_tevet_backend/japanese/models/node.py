from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from common.db_fields.schema_field import SchemaField
from japanese.enums.jlpt_level import JlptLevel
from japanese.enums.node_status import NodeStatus
from japanese.enums.node_type import NodeType
from japanese.schemas.kanji_schema import KanjiSchema
from japanese.schemas.particle_schema import ParticleSchema
from japanese.schemas.passage_schema import PassageSchema
from japanese.schemas.rule_schema import RuleSchema
from japanese.schemas.sentence_schema import SentenceSchema
from japanese.schemas.word_schema import WordSchema

if TYPE_CHECKING:
    from japanese.models.generation_log import GenerationLog
    from japanese.models.node_edge import NodeEdge
    from japanese.models.user_node_state import UserNodeState


class Node(models.Model):
    if TYPE_CHECKING:
        id: int
        generation_logs: Manager['GenerationLog']
        outgoing_edges: Manager['NodeEdge']
        incoming_edges: Manager['NodeEdge']
        user_states: Manager['UserNodeState']

    list_display = ['id', 'type', 'status', 'canonical_key', 'jlpt_level']
    list_filter = ['type', 'status', 'jlpt_level']

    type: NodeType = models.CharField(
        max_length=32,
        choices=NodeType.choices(),
    )
    status: NodeStatus = models.CharField(
        max_length=32,
        choices=NodeStatus.choices(),
        default=NodeStatus.STUB,
        blank=True,
    )
    canonical_key = models.CharField(max_length=255)
    jlpt_level: JlptLevel | None = models.CharField(
        max_length=8,
        choices=JlptLevel.choices(),
        null=True,
        blank=True,
        default=None,
    )

    content_html = models.TextField(default='', blank=True)
    notes = models.TextField(default='', blank=True)

    sentence_data: SentenceSchema | None = SchemaField(
        SentenceSchema, null=True, blank=True, default=None
    )
    word_data: WordSchema | None = SchemaField(
        WordSchema, null=True, blank=True, default=None
    )
    kanji_data: KanjiSchema | None = SchemaField(
        KanjiSchema, null=True, blank=True, default=None
    )
    particle_data: ParticleSchema | None = SchemaField(
        ParticleSchema, null=True, blank=True, default=None
    )
    rule_data: RuleSchema | None = SchemaField(
        RuleSchema, null=True, blank=True, default=None
    )
    passage_data: PassageSchema | None = SchemaField(
        PassageSchema, null=True, blank=True, default=None
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['type', 'canonical_key'],
                name='japanese_node_unique_type_canonical_key',
            ),
        ]
        indexes = [
            models.Index(fields=['type', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f'{self.type}: {self.canonical_key}'
