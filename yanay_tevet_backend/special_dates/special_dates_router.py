from common.django_utils.api_router_creator import ApiRouterCreator
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from special_dates.views.calendar_views.create_special_date_calendar_view import CreateSpecialDateCalendarView
from special_dates.views.calendar_views.delete_special_date_calendar_view import DeleteSpecialDateCalendarView
from special_dates.views.calendar_views.join_special_date_calendar_view import JoinSpecialDateCalendarView
from special_dates.views.calendar_views.leave_special_date_calendar_view import LeaveSpecialDateCalendarView
from special_dates.views.calendar_views.list_special_date_calendar_members_view import ListSpecialDateCalendarMembersView
from special_dates.views.calendar_views.list_special_date_calendars_view import ListSpecialDateCalendarsView
from special_dates.views.calendar_views.remove_special_date_calendar_member_view import RemoveSpecialDateCalendarMemberView
from special_dates.views.calendar_views.rename_special_date_calendar_view import RenameSpecialDateCalendarView
from special_dates.views.calendar_views.reset_special_date_calendar_link_view import ResetSpecialDateCalendarLinkView
from special_dates.views.calendar_views.share_special_date_calendar_view import ShareSpecialDateCalendarView
from special_dates.views.calendar_views.update_special_date_calendar_preferences_view import (
    UpdateSpecialDateCalendarPreferencesView,
)
from special_dates.views.special_date_views.convert_special_date_view import ConvertSpecialDateView
from special_dates.views.special_date_views.create_special_date_view import CreateSpecialDateView
from special_dates.views.special_date_views.delete_special_date_view import DeleteSpecialDateView
from special_dates.views.special_date_views.get_hebrew_year_view import GetHebrewYearView
from special_dates.views.special_date_views.get_upcoming_special_dates_view import GetUpcomingSpecialDatesView
from special_dates.views.special_date_views.move_special_dates_view import MoveSpecialDatesView
from special_dates.views.special_date_views.paginate_special_dates_view import PaginateSpecialDatesView
from special_dates.views.special_date_views.update_special_date_view import UpdateSpecialDateView

api, router = ApiRouterCreator.create_api_and_router('special-dates', LoginPermissionChecker())

# --- Events ---
PaginateSpecialDatesView.register_get(router, 'dates/')
CreateSpecialDateView.register_post(router, 'dates/')
MoveSpecialDatesView.register_post(router, 'dates/move/')
UpdateSpecialDateView.register_patch_by_id(router, prefix='dates')
DeleteSpecialDateView.register_delete_by_id(router, prefix='dates')
GetUpcomingSpecialDatesView.register_get(router, 'upcoming/')
ConvertSpecialDateView.register_get(router, 'convert/')
GetHebrewYearView.register_get(router, 'hebrew-year/')

# --- Calendars ---
ListSpecialDateCalendarsView.register_get(router, 'calendars/')
CreateSpecialDateCalendarView.register_post(router, 'calendars/')
JoinSpecialDateCalendarView.register_post(router, 'calendars/join/')
DeleteSpecialDateCalendarView.register_delete_by_id(router, prefix='calendars')
RenameSpecialDateCalendarView.register_post(router, 'calendars/{int:object_id}/rename/')
ShareSpecialDateCalendarView.register_post(router, 'calendars/{int:object_id}/share/')
RemoveSpecialDateCalendarMemberView.register_post(router, 'calendars/{int:object_id}/remove-member/')
LeaveSpecialDateCalendarView.register_post(router, 'calendars/{int:object_id}/leave/')
ResetSpecialDateCalendarLinkView.register_post(router, 'calendars/{int:object_id}/reset-link/')
UpdateSpecialDateCalendarPreferencesView.register_post(router, 'calendars/{int:object_id}/preferences/')
ListSpecialDateCalendarMembersView.register_get(router, 'calendars/{int:object_id}/members/')
