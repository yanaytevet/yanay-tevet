from shopping_lists.permissions_checkers.shopping_lists_permission_checker import ShoppingListsPermissionChecker
from shopping_lists.views.list_views.create_shopping_list_view import CreateShoppingListView
from shopping_lists.views.list_views.delete_shopping_list_view import DeleteShoppingListView
from shopping_lists.views.list_views.get_shopping_list_view import GetShoppingListView
from shopping_lists.views.list_views.list_shopping_list_members_view import ListShoppingListMembersView
from shopping_lists.views.list_views.paginate_shopping_lists_view import PaginateShoppingListsView
from shopping_lists.views.list_views.share_shopping_list_view import ShareShoppingListView
from shopping_lists.views.list_views.unshare_shopping_list_view import UnshareShoppingListView
from shopping_lists.views.list_views.update_shopping_list_view import UpdateShoppingListView
from shopping_lists.views.item_views.create_shopping_item_view import CreateShoppingItemView
from shopping_lists.views.item_views.delete_shopping_item_view import DeleteShoppingItemView
from shopping_lists.views.item_views.paginate_shopping_items_view import PaginateShoppingItemsView
from shopping_lists.views.item_views.update_shopping_item_view import UpdateShoppingItemView
from common.django_utils.api_router_creator import ApiRouterCreator

api, router = ApiRouterCreator.create_api_and_router('shopping-lists', ShoppingListsPermissionChecker())

# --- Lists ---
PaginateShoppingListsView.register_get(router, 'lists/')
CreateShoppingListView.register_post(router, 'lists/')
GetShoppingListView.register_get(router, 'lists/{int:object_id}/')
UpdateShoppingListView.register_patch_by_id(router, prefix='lists')
DeleteShoppingListView.register_delete_by_id(router, prefix='lists')
ShareShoppingListView.register_post(router, 'lists/{int:object_id}/share/')
UnshareShoppingListView.register_post(router, 'lists/{int:object_id}/unshare/')
ListShoppingListMembersView.register_get(router, 'lists/{int:object_id}/members/')

# --- Items ---
PaginateShoppingItemsView.register_get(router, 'lists/{int:list_id}/items/')
CreateShoppingItemView.register_post(router, 'items/')
UpdateShoppingItemView.register_patch_by_id(router, prefix='items')
DeleteShoppingItemView.register_delete_by_id(router, prefix='items')
