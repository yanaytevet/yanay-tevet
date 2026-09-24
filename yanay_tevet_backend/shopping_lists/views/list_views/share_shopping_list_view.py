from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from shopping_lists.managers.shopping_list_manager import ShoppingListManager
from shopping_lists.models.shopping_list import ShoppingList
from shopping_lists.permissions_checkers.shopping_list_member_permission_checker import (
    ShoppingListMemberPermissionChecker,
)
from shopping_lists.serializers.shopping_list_serializers.shopping_list_serializer import ShoppingListSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.run_action_views.run_action_on_item_by_id_api_view import RunActionOnItemByIdAPIView


class ShareShoppingListSchema(Schema):
    identifier: str


class ShareShoppingListView(RunActionOnItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ShoppingList

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ShoppingListSerializer()

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ShareShoppingListSchema

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ShoppingList, data: Schema, path: Path) -> None:
        await ShoppingListMemberPermissionChecker(obj, require_owner=True).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def run_action(cls, request: APIRequest, obj: ShoppingList, data: ShareShoppingListSchema, path: Path) -> None:
        user = await request.future_user
        await ShoppingListManager(user).share(obj, data.identifier)
        return None
