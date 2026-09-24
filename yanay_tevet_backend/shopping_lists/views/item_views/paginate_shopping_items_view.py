from typing import Type

from django.db.models import F, Model, QuerySet
from ninja import FilterSchema, Path, Query, Schema

from shopping_lists.models.shopping_item import ShoppingItem
from shopping_lists.models.shopping_list import ShoppingList
from shopping_lists.permissions_checkers.shopping_list_member_permission_checker import (
    ShoppingListMemberPermissionChecker,
)
from shopping_lists.serializers.shopping_item_serializers.shopping_item_serializer import ShoppingItemSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class ShoppingItemsByListPath(Schema):
    list_id: int


class PaginateShoppingItemsFilterSchema(FilterSchema):
    is_checked: bool | None = None


class PaginateShoppingItemsView(PaginateItemsAPIView):
    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ShoppingItemsByListPath

    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        shopping_list = await ShoppingList.objects.filter(id=path.list_id).afirst()
        if shopping_list is None:
            raise ObjectDoesntExistAPIException(ShoppingList, path.list_id)
        await ShoppingListMemberPermissionChecker(shopping_list).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ShoppingItemSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'order', 'name', 'checked_at', 'updated_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateShoppingItemsFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ShoppingItem

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        return queryset.filter(shopping_list_id=path.list_id).order_by(
            'is_checked', 'order', F('checked_at').desc(nulls_last=True), 'id'
        )
