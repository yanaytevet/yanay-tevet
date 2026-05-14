from typing import Type

from django.db.models import Model
from ninja import Schema, Path

from blocks.enums.block_types import BlockTypes
from blocks.models import Block
from blocks.serializers.blocks_serializers.block_serializer import BlockSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateBlockItemSchema(Schema):
    a: str
    b: int
    c: bool
    block_type: BlockTypes


class PostCreateBlockItemView(CreateItemAPIView):
    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: Schema, path: Path) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateBlockItemSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return BlockSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Block
