from typing import Type

from django.db.models import Model
from ninja import Path, Query

from shopping_lists.models.shopping_list import ShoppingList
from shopping_lists.permissions_checkers.shopping_list_member_permission_checker import (
    ShoppingListMemberPermissionChecker,
)
from shopping_lists.serializers.shopping_list_serializers.shopping_list_serializer import ShoppingListSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_by_id_api_view import ReadItemByIdAPIView


class GetShoppingListView(ReadItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ShoppingList

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ShoppingListSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ShoppingList, query: Query, path: Path) -> None:
        await ShoppingListMemberPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)
