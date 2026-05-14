from typing import Type, Optional

from django.db.models import Model
from ninja import Schema, Path

from blocks.models import Block
from blocks.serializers.blocks_serializers.block_serializer import BlockSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView


class PatchBlockItemSchema(Schema):
    a: Optional[str]
    b: Optional[float]
    c: Optional[bool]


class UpdateBlockItemView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return PatchBlockItemSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return BlockSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Block

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Model, data: Schema, path: Path) -> None:
        pass
