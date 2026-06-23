from itinerary_lists.permissions_checkers.itinerary_lists_permission_checker import ItineraryListsPermissionChecker
from itinerary_lists.views.list_views.create_itinerary_list_view import CreateItineraryListView
from itinerary_lists.views.list_views.delete_itinerary_list_view import DeleteItineraryListView
from itinerary_lists.views.list_views.get_itinerary_list_view import GetItineraryListView
from itinerary_lists.views.list_views.list_itinerary_list_members_view import ListItineraryListMembersView
from itinerary_lists.views.list_views.paginate_itinerary_lists_view import PaginateItineraryListsView
from itinerary_lists.views.list_views.set_itinerary_list_status_view import (
    ActivateItineraryListView,
    FinishItineraryListView,
)
from itinerary_lists.views.list_views.share_itinerary_list_view import ShareItineraryListView
from itinerary_lists.views.list_views.unshare_itinerary_list_view import UnshareItineraryListView
from itinerary_lists.views.list_views.update_itinerary_list_view import UpdateItineraryListView
from itinerary_lists.views.item_views.create_itinerary_item_view import CreateItineraryItemView
from itinerary_lists.views.item_views.delete_itinerary_item_view import DeleteItineraryItemView
from itinerary_lists.views.item_views.get_itinerary_item_view import GetItineraryItemView
from itinerary_lists.views.item_views.paginate_itinerary_items_view import PaginateItineraryItemsView
from itinerary_lists.views.item_views.update_itinerary_item_view import UpdateItineraryItemView
from itinerary_lists.views.task_views.create_itinerary_task_view import CreateItineraryTaskView
from itinerary_lists.views.task_views.delete_itinerary_task_view import DeleteItineraryTaskView
from itinerary_lists.views.task_views.get_itinerary_task_view import GetItineraryTaskView
from itinerary_lists.views.task_views.paginate_itinerary_tasks_view import PaginateItineraryTasksView
from itinerary_lists.views.task_views.update_itinerary_task_view import UpdateItineraryTaskView
from common.django_utils.api_router_creator import ApiRouterCreator

api, router = ApiRouterCreator.create_api_and_router('itinerary-lists', ItineraryListsPermissionChecker())

# --- Lists ---
PaginateItineraryListsView.register_get(router, 'lists/')
CreateItineraryListView.register_post(router, 'lists/')
GetItineraryListView.register_get(router, 'lists/{int:object_id}/')
UpdateItineraryListView.register_patch_by_id(router, prefix='lists')
DeleteItineraryListView.register_delete_by_id(router, prefix='lists')
ShareItineraryListView.register_post(router, 'lists/{int:object_id}/share/')
UnshareItineraryListView.register_post(router, 'lists/{int:object_id}/unshare/')
ListItineraryListMembersView.register_get(router, 'lists/{int:object_id}/members/')
ActivateItineraryListView.register_post(router, 'lists/{int:object_id}/activate/')
FinishItineraryListView.register_post(router, 'lists/{int:object_id}/finish/')

# --- Items ---
PaginateItineraryItemsView.register_get(router, 'lists/{int:list_id}/items/')
CreateItineraryItemView.register_post(router, 'items/')
GetItineraryItemView.register_get(router, 'items/{int:object_id}/')
UpdateItineraryItemView.register_patch_by_id(router, prefix='items')
DeleteItineraryItemView.register_delete_by_id(router, prefix='items')

# --- Tasks ---
PaginateItineraryTasksView.register_get(router, 'lists/{int:list_id}/tasks/')
CreateItineraryTaskView.register_post(router, 'tasks/')
GetItineraryTaskView.register_get(router, 'tasks/{int:object_id}/')
UpdateItineraryTaskView.register_patch_by_id(router, prefix='tasks')
DeleteItineraryTaskView.register_delete_by_id(router, prefix='tasks')
