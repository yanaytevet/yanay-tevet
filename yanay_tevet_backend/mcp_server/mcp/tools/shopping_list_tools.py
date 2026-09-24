from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from mcp_server.mcp.context import get_current_user
from mcp_server.mcp.schemas.shopping_list_schemas import (
    DeletedShoppingItemsResult,
    ShoppingItemChange,
    ShoppingListDetails,
)
from mcp_server.mcp.tool_errors import handle_tool_errors
from shopping_lists.managers.shopping_item_manager import ShoppingItemManager
from shopping_lists.managers.shopping_list_manager import ShoppingListManager
from shopping_lists.models.shopping_item import ShoppingItem
from shopping_lists.models.shopping_list import ShoppingList
from shopping_lists.permissions_checkers.shopping_list_member_permission_checker import (
    ShoppingListMemberPermissionChecker,
)
from shopping_lists.permissions_checkers.shopping_lists_permission_checker import ShoppingListsPermissionChecker
from shopping_lists.serializers.shopping_item_serializers.shopping_item_serializer import (
    ShoppingItemSchema,
    ShoppingItemSerializer,
    ShoppingItemWritableSchema,
)
from shopping_lists.serializers.shopping_list_serializers.shopping_list_serializer import (
    ShoppingListSchema,
    ShoppingListSerializer,
)
from users.models import User

READ_ONLY = ToolAnnotations(readOnlyHint=True)
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False)
DESTRUCTIVE = ToolAnnotations(readOnlyHint=False, destructiveHint=True)


async def _get_user() -> User:
    """The connected user, provided they have the Shopping Lists app (the web API applies the same
    check at router level)."""
    user = await get_current_user()
    await ShoppingListsPermissionChecker().async_raise_exception_if_not_valid(user)
    return user


async def _load_list(user: User, list_id: int) -> ShoppingList:
    shopping_list = await ShoppingList.objects.filter(id=list_id).afirst()
    if shopping_list is None:
        raise ObjectDoesntExistAPIException(ShoppingList, list_id)
    await ShoppingListMemberPermissionChecker(shopping_list).async_raise_exception_if_not_valid(user)
    return shopping_list


async def _load_items(user: User, item_ids: list[int]) -> list[ShoppingItem]:
    """Load every requested item and check access to each one's list up front, so a batch either
    passes validation as a whole or changes nothing."""
    unique_ids = list(dict.fromkeys(item_ids))
    by_id = {item.id: item async for item in ShoppingItem.objects.filter(id__in=unique_ids)}
    for item_id in unique_ids:
        if item_id not in by_id:
            raise ObjectDoesntExistAPIException(ShoppingItem, item_id)
    for list_id in {item.shopping_list_id for item in by_id.values()}:
        await _load_list(user, list_id)
    return [by_id[item_id] for item_id in unique_ids]


async def _list_details(shopping_list: ShoppingList, include_checked: bool) -> ShoppingListDetails:
    items = ShoppingItem.objects.filter(shopping_list_id=shopping_list.id).order_by('is_checked', 'order', 'id')
    if not include_checked:
        items = items.filter(is_checked=False)
    return ShoppingListDetails(
        shopping_list=await ShoppingListSerializer().serialize(shopping_list),
        items=await ShoppingItemSerializer().serialize_query(items),
    )


def register(mcp: FastMCP) -> None:
    @mcp.tool(annotations=READ_ONLY)
    @handle_tool_errors
    async def list_shopping_lists() -> list[ShoppingListSchema]:
        """List the shopping lists you're a member of (owned or shared with you), most recently
        updated first, with item counts and a preview of the unchecked items."""
        user = await _get_user()
        lists = ShoppingList.objects.filter(memberships__user_id=user.id).distinct().order_by('-updated_at')
        return await ShoppingListSerializer().serialize_query(lists)

    @mcp.tool(annotations=READ_ONLY)
    @handle_tool_errors
    async def get_shopping_list(list_id: int, include_checked: bool = False) -> ShoppingListDetails:
        """Get a shopping list and its items. Checked-off items (already bought) are left out unless
        include_checked is true."""
        user = await _get_user()
        shopping_list = await _load_list(user, list_id)
        return await _list_details(shopping_list, include_checked)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def create_shopping_list(name: str, item_names: list[str] | None = None) -> ShoppingListDetails:
        """Create a new shopping list owned by you, optionally with initial items."""
        user = await _get_user()
        shopping_list = await ShoppingListManager(user).create_list(name)
        item_manager = ShoppingItemManager(user)
        for item_name in item_names or []:
            await item_manager.add_item(shopping_list.id, item_name)
        return await _list_details(shopping_list, include_checked=False)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def rename_shopping_list(list_id: int, name: str) -> ShoppingListSchema:
        """Rename a shopping list."""
        user = await _get_user()
        shopping_list = await _load_list(user, list_id)
        await ShoppingListManager(user).rename(shopping_list, name)
        return await ShoppingListSerializer().serialize(shopping_list)

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def add_shopping_items(list_id: int, item_names: list[str]) -> list[ShoppingItemSchema]:
        """Add items to a shopping list by name. Names are matched case-insensitively against the list:
        an item that's already on the list unchecked is not duplicated, and one that was checked off
        is un-checked (put back on the list) instead of being added again."""
        user = await _get_user()
        shopping_list = await _load_list(user, list_id)
        item_manager = ShoppingItemManager(user)
        items = [await item_manager.add_item(shopping_list.id, item_name) for item_name in item_names]
        serializer = ShoppingItemSerializer()
        return [await serializer.serialize(item) for item in items]

    @mcp.tool(annotations=WRITE)
    @handle_tool_errors
    async def update_shopping_items(changes: list[ShoppingItemChange]) -> list[ShoppingItemSchema]:
        """Check off (is_checked true — bought), un-check, or rename one or more items. Only the fields
        included for each item are changed."""
        user = await _get_user()
        items = {item.id: item for item in await _load_items(user, [change.item_id for change in changes])}
        item_manager = ShoppingItemManager(user)
        for change in changes:
            await item_manager.update_item(
                items[change.item_id], ShoppingItemWritableSchema(name=change.name, is_checked=change.is_checked),
            )
        serializer = ShoppingItemSerializer()
        return [await serializer.serialize(item) for item in items.values()]

    @mcp.tool(annotations=DESTRUCTIVE)
    @handle_tool_errors
    async def delete_shopping_items(item_ids: list[int]) -> DeletedShoppingItemsResult:
        """Permanently delete items from their shopping lists. To mark something as bought, check it off
        with update_shopping_items instead — checked items stay available as suggestions."""
        user = await _get_user()
        items = await _load_items(user, item_ids)
        # Captured up front: Django clears an instance's id once it is deleted.
        deleted_ids = [item.id for item in items]
        item_manager = ShoppingItemManager(user)
        for item in items:
            await item_manager.delete_item(item)
        return DeletedShoppingItemsResult(deleted_item_ids=deleted_ids)
