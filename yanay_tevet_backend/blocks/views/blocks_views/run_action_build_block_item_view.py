from typing import Type

from django.db.models import Model
from ninja import Schema, Path

from blocks.models import Block
from blocks.serializers.blocks_serializers.block_serializer import BlockSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.run_action_views.run_action_on_item_by_id_api_view import RunActionOnItemByIdAPIView


class RunActionBuildBlockItemSchema(Schema):
    should_build: bool


class RunActionBuildBlockItemView(RunActionOnItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return RunActionBuildBlockItemSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return BlockSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: RunActionBuildBlockItemSchema, path: Path
                                            ) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Block, data: RunActionBuildBlockItemSchema,
                                           path: Path) -> None:
        pass

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Block

    @classmethod
    async def run_action(cls, request: APIRequest, obj: Block, data: RunActionBuildBlockItemSchema, path: Path
                         ) -> Schema | None:
        if data.should_build:
            obj.a += ' build'
        else:
            obj.a += ' not build'
        await obj.asave()
