from django.db.models import Max

from shopping_lists.models.shopping_item import ShoppingItem
from shopping_lists.models.shopping_list import ShoppingList
from shopping_lists.serializers.shopping_item_serializers.shopping_item_serializer import (
    ShoppingItemWritableSchema,
)
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.time_utils import TimeUtils
from users.models import User


class ShoppingItemManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def add_item(self, shopping_list_id: int, name: str) -> ShoppingItem:
        """Add an item by name, reusing an existing item with the same name when there is one.

        A matching checked item is un-checked and moved to the bottom of the list, which is how
        picking an autocomplete suggestion (sourced from the checked items) brings it back.
        A matching unchecked item is returned as-is so the list never shows the same thing twice.
        """
        name = self._clean_name(name)
        existing = await ShoppingItem.objects.filter(
            shopping_list_id=shopping_list_id, name__iexact=name
        ).order_by('is_checked', '-updated_at').afirst()
        if existing is not None:
            if existing.is_checked:
                await self._uncheck(existing)
                await existing.asave()
                await self._touch_list(shopping_list_id)
            return existing

        item = ShoppingItem(
            shopping_list_id=shopping_list_id,
            created_by_id=self.user.id,
            name=name,
            order=await self._next_order(shopping_list_id),
        )
        await item.asave()
        await self._touch_list(shopping_list_id)
        return item

    async def update_item(self, item: ShoppingItem, writable: ShoppingItemWritableSchema) -> None:
        if writable.name is not None:
            item.name = self._clean_name(writable.name)
        if writable.is_checked is not None and writable.is_checked != item.is_checked:
            if writable.is_checked:
                item.is_checked = True
                item.checked_at = TimeUtils.now()
            else:
                await self._uncheck(item)
        await item.asave()
        await self._touch_list(item.shopping_list_id)

    async def delete_item(self, item: ShoppingItem) -> None:
        shopping_list_id = item.shopping_list_id
        await item.adelete()
        await self._touch_list(shopping_list_id)

    async def _uncheck(self, item: ShoppingItem) -> None:
        item.is_checked = False
        item.checked_at = None
        item.order = await self._next_order(item.shopping_list_id)

    @classmethod
    def _clean_name(cls, name: str) -> str:
        cleaned = name.strip()
        if not cleaned:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='Item name cannot be empty.',
                error_code='empty_item_name',
            )
        return cleaned

    async def _touch_list(self, shopping_list_id: int) -> None:
        await ShoppingList.objects.filter(id=shopping_list_id).aupdate(updated_at=TimeUtils.now())

    async def _next_order(self, shopping_list_id: int) -> int:
        aggregate = await ShoppingItem.objects.filter(
            shopping_list_id=shopping_list_id, is_checked=False
        ).aaggregate(max_order=Max('order'))
        current_max = aggregate['max_order']
        return 0 if current_max is None else current_max + 1
