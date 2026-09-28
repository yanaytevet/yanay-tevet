from common.django_utils.api_router_creator import ApiRouterCreator
from special_dates.views.calendar_views.get_special_date_calendar_join_preview_view import (
    GetSpecialDateCalendarJoinPreviewView,
)

# No login required: a join link must be viewable before signing in / registering.
api, router = ApiRouterCreator.create_api_and_router('special-dates-public')

GetSpecialDateCalendarJoinPreviewView.register_get(router, 'join-preview/')
