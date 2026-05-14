from typing import Type, Optional

from django.db.models import Model
from ninja import Query, Path, FilterSchema
from pydantic import Field

from blocks.enums.block_types import BlockTypes
from blocks.models import Block
from blocks.serializers.blocks_serializers.block_serializer import BlockSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class PaginationBlockFilterSchema(FilterSchema):
    a: Optional[str] = None
    c: Optional[str] = None
    search: Optional[str] = Field(None, q=[
        'a__icontains', 'b__icontains', 'block_type__icontains'])
    block_type: Optional[BlockTypes] = None


class PaginationBlockView(PaginateItemsAPIView):
    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    def get_serializer(cls) -> Serializer:
        return BlockSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'a', 'b', 'c'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginationBlockFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Block
