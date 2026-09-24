from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from shopping_lists.managers.shopping_item_manager import ShoppingItemManager
from shopping_lists.models.shopping_item import ShoppingItem
from shopping_lists.models.shopping_list import ShoppingList
from shopping_lists.permissions_checkers.shopping_list_member_permission_checker import (
    ShoppingListMemberPermissionChecker,
)
from shopping_lists.serializers.shopping_item_serializers.shopping_item_serializer import ShoppingItemSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateShoppingItemSchema(Schema):
    shopping_list_id: int
    name: str


class CreateShoppingItemView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateShoppingItemSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ShoppingItemSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ShoppingItem

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateShoppingItemSchema, path: Path) -> None:
        shopping_list = await ShoppingList.objects.filter(id=data.shopping_list_id).afirst()
        if shopping_list is None:
            raise ObjectDoesntExistAPIException(ShoppingList, data.shopping_list_id)
        await ShoppingListMemberPermissionChecker(shopping_list).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreateShoppingItemSchema, path: Path) -> Model:
        user = await request.future_user
        return await ShoppingItemManager(user).add_item(data.shopping_list_id, data.name)
