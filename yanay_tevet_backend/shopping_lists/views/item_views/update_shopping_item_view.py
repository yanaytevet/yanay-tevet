from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from shopping_lists.managers.shopping_item_manager import ShoppingItemManager
from shopping_lists.models.shopping_item import ShoppingItem
from shopping_lists.permissions_checkers.shopping_list_member_permission_checker import (
    ShoppingListMemberPermissionChecker,
)
from shopping_lists.serializers.shopping_item_serializers.shopping_item_serializer import (
    ShoppingItemSerializer,
    ShoppingItemWritableSchema,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView


class UpdateShoppingItemView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ShoppingItemWritableSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ShoppingItemSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ShoppingItem

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ShoppingItem, data: Schema, path: Path) -> None:
        shopping_list = await obj.get_shopping_list()
        await ShoppingListMemberPermissionChecker(shopping_list).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def update_object(cls, request: APIRequest, obj: ShoppingItem, data: ShoppingItemWritableSchema, path: Path) -> None:
        user = await request.future_user
        await ShoppingItemManager(user).update_item(obj, data)
