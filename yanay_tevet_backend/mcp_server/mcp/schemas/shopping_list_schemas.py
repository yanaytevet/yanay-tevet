from typing import Optional

from ninja import Schema

from shopping_lists.serializers.shopping_item_serializers.shopping_item_serializer import ShoppingItemSchema
from shopping_lists.serializers.shopping_list_serializers.shopping_list_serializer import ShoppingListSchema


class ShoppingItemChange(Schema):
    """Only the fields you include are changed."""
    item_id: int
    name: Optional[str] = None
    is_checked: Optional[bool] = None


class ShoppingListDetails(Schema):
    shopping_list: ShoppingListSchema
    # Unchecked items first, in list order.
    items: list[ShoppingItemSchema]


class DeletedShoppingItemsResult(Schema):
    deleted_item_ids: list[int]
