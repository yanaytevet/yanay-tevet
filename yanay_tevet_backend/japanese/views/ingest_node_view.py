from typing import Type

from ninja import Schema, Path

from common.async_utils.background_task_runner import run_in_background
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from japanese.llm.content_service import ContentGenerationService
from japanese.llm.ingest_service import IngestService
from japanese.serializers.node_detail_serializer import NodeDetailSchema, NodeDetailSerializer
from users.permissions_checkers.admin_permissions_checker import AdminPermissionsChecker


class IngestNodeSchema(Schema):
    text: str


class IngestNodeView(SimplePostAPIView):
    @classmethod
    async def check_permitted(cls, request: APIRequest, data: IngestNodeSchema, path: Path = None) -> None:
        await AdminPermissionsChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def run_action(cls, request: APIRequest, data: IngestNodeSchema, path: Path = None) -> NodeDetailSchema:
        node = await IngestService.ingest(data.text)
        run_in_background(ContentGenerationService.generate_for_node(node))
        serializer: Serializer = NodeDetailSerializer()
        return await serializer.inner_serialize(node)

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return NodeDetailSchema

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return IngestNodeSchema
