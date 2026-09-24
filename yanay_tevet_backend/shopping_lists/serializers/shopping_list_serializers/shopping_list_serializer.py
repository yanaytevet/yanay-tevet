from datetime import datetime

from ninja import Schema

from shopping_lists.models.shopping_list import ShoppingList
from common.simple_api.serializers.serializer import Serializer

PREVIEW_ITEMS_COUNT = 6


class ShoppingListSchema(Schema):
    id: int
    name: str
    owner_id: int
    owner_username: str
    member_count: int
    unchecked_count: int
    checked_count: int
    preview_items: list[str]
    created_at: datetime
    updated_at: datetime


class ShoppingListSerializer(Serializer[ShoppingListSchema]):
    async def inner_serialize(self, obj: ShoppingList) -> ShoppingListSchema:
        owner = await obj.get_owner()
        member_count = await obj.memberships.acount()
        unchecked = obj.items.filter(is_checked=False)
        unchecked_count = await unchecked.acount()
        checked_count = await obj.items.filter(is_checked=True).acount()
        preview_items = [
            name async for name in unchecked.order_by('order', 'id').values_list('name', flat=True)[:PREVIEW_ITEMS_COUNT]
        ]
        return ShoppingListSchema(
            id=obj.id,
            name=obj.name,
            owner_id=obj.owner_id,
            owner_username=owner.username if owner else '',
            member_count=member_count,
            unchecked_count=unchecked_count,
            checked_count=checked_count,
            preview_items=preview_items,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
