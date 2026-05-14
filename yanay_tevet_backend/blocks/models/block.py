from typing import TYPE_CHECKING
from django.db import models

from blocks.enums.block_types import BlockTypes


class Block(models.Model):
    if TYPE_CHECKING:
        id: int

    list_filter = []
    a = models.TextField(default="", blank=True)
    b = models.IntegerField(default=0, blank=True)
    c = models.BooleanField(default=False, blank=True)
    block_type: BlockTypes = models.CharField(
        max_length=255,
        choices=BlockTypes.choices(),
        blank=True,
        default=BlockTypes.ROUND,
    )
