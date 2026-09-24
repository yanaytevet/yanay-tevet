from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from shopping_lists.managers.shopping_item_manager import ShoppingItemManager
from shopping_lists.models.shopping_item import ShoppingItem
from shopping_lists.permissions_checkers.shopping_list_member_permission_checker import (
    ShoppingListMemberPermissionChecker,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView


class DeleteShoppingItemView(DeleteItemByIdAPIView):
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
    async def delete_object(cls, request: APIRequest, obj: ShoppingItem, data: Schema, path: Path) -> None:
        user = await request.future_user
        await ShoppingItemManager(user).delete_item(obj)
