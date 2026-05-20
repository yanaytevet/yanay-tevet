from typing import Type

from django.db.models import Model
from ninja import Query, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_by_id_api_view import ReadItemByIdAPIView
from japanese.enums.node_status import NodeStatus
from japanese.models.node import Node
from japanese.serializers.node_detail_serializer import NodeDetailSerializer


class ReadNodeView(ReadItemByIdAPIView):
    @classmethod
    def get_serializer(cls) -> Serializer:
        return NodeDetailSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Node

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Node, query: Query, path: Path) -> None:
        if obj.status == NodeStatus.PUBLISHED:
            return
        user = await request.future_user
        if user is None or user.is_anonymous or not user.is_admin():
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message='Node not found.',
                error_code='node_not_found',
            )
