from typing import Type

from django.db.models import Model
from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.run_action_views.run_action_on_item_by_id_api_view import (
    RunActionOnItemByIdAPIView,
)
from japanese.llm.content_service import ContentGenerationService
from japanese.models.node import Node
from japanese.schemas.generate_content_input_schema import GenerateContentInputSchema
from japanese.serializers.node_detail_serializer import NodeDetailSerializer
from users.permissions_checkers.admin_permissions_checker import AdminPermissionsChecker


class GenerateContentView(RunActionOnItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return GenerateContentInputSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return NodeDetailSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Node

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        await AdminPermissionsChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Node, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def run_action(cls, request: APIRequest, obj: Node, data: GenerateContentInputSchema, path: Path) -> Schema | None:
        surviving = await ContentGenerationService.generate_for_node(obj, user_note=data.user_note)
        # The node may have been merged into an existing canonical node — serialize the surviving one.
        return await cls.get_serializer().serialize(surviving)
