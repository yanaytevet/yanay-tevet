from ninja import Schema

from blocks.enums.block_types import BlockTypes
from blocks.models import Block
from common.simple_api.serializers.serializer import Serializer


class FullBlockOutput(Schema):
    id: int
    a: str
    b: int
    c: bool
    block_type: BlockTypes
    another_field: str


class FullBlockSerializer(Serializer[FullBlockOutput]):
    async def inner_serialize(self, obj: Block) -> FullBlockOutput:
        return FullBlockOutput(
            id=obj.id,
            a=obj.a,
            b=obj.b,
            c=obj.c,
            block_type=obj.block_type,
            another_field="another_value",
        )
