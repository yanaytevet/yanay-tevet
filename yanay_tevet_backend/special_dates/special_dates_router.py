from common.django_utils.api_router_creator import ApiRouterCreator
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from special_dates.views.special_date_views.create_special_date_view import CreateSpecialDateView
from special_dates.views.special_date_views.delete_special_date_view import DeleteSpecialDateView
from special_dates.views.special_date_views.get_hebrew_date_view import GetHebrewDateView
from special_dates.views.special_date_views.get_upcoming_special_dates_view import GetUpcomingSpecialDatesView
from special_dates.views.special_date_views.paginate_special_dates_view import PaginateSpecialDatesView
from special_dates.views.special_date_views.update_special_date_view import UpdateSpecialDateView

api, router = ApiRouterCreator.create_api_and_router('special-dates', LoginPermissionChecker())

PaginateSpecialDatesView.register_get(router, 'dates/')
CreateSpecialDateView.register_post(router, 'dates/')
UpdateSpecialDateView.register_patch_by_id(router, prefix='dates')
DeleteSpecialDateView.register_delete_by_id(router, prefix='dates')
GetUpcomingSpecialDatesView.register_get(router, 'upcoming/')
GetHebrewDateView.register_get(router, 'hebrew-date/')
