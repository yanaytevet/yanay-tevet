from typing import Type

from ninja import Query, Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from japanese.enums.node_status import NodeStatus
from japanese.models.node import Node
from japanese.serializers.node_summary_serializer import (
    NodeSummarySchema,
    NodeSummarySerializer,
)
from users.permissions_checkers.admin_permissions_checker import AdminPermissionsChecker


class GetReviewQueueResponseSchema(Schema):
    stubs: list[NodeSummarySchema]
    needs_review: list[NodeSummarySchema]


class GetReviewQueueView(SimpleGetAPIView):
    @classmethod
    async def check_permitted(cls, request: APIRequest, query: Query = None, path: Path = None) -> None:
        await AdminPermissionsChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def get_data(
        cls, request: APIRequest, query: Query = None, path: Path = None
    ) -> GetReviewQueueResponseSchema:
        serializer = NodeSummarySerializer()
        stubs = await serializer.serialize_query(
            Node.objects.filter(status=NodeStatus.STUB).order_by('-created_at')[:100]
        )
        needs_review = await serializer.serialize_query(
            Node.objects.filter(status=NodeStatus.NEEDS_REVIEW).order_by('-updated_at')[:100]
        )
        return GetReviewQueueResponseSchema(stubs=stubs, needs_review=needs_review)

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return GetReviewQueueResponseSchema
