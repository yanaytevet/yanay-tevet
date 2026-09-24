from datetime import datetime
from typing import Optional

from ninja import Schema

from shopping_lists.models.shopping_item import ShoppingItem
from common.simple_api.serializers.serializer import Serializer


class ShoppingItemSchema(Schema):
    id: int
    shopping_list_id: int
    name: str
    is_checked: bool
    checked_at: Optional[datetime]
    order: int
    created_at: datetime
    updated_at: datetime


class ShoppingItemWritableSchema(Schema):
    name: Optional[str] = None
    is_checked: Optional[bool] = None


class ShoppingItemSerializer(Serializer[ShoppingItemSchema]):
    async def inner_serialize(self, obj: ShoppingItem) -> ShoppingItemSchema:
        return ShoppingItemSchema(
            id=obj.id,
            shopping_list_id=obj.shopping_list_id,
            name=obj.name,
            is_checked=obj.is_checked,
            checked_at=obj.checked_at,
            order=obj.order,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
