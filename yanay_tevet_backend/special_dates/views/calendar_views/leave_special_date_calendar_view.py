from typing import Type

from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.models.special_date_calendar import SpecialDateCalendar
from special_dates.views.calendar_views.special_date_calendar_action_view import SpecialDateCalendarActionView


class LeaveSpecialDateCalendarView(SpecialDateCalendarActionView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    async def run_action(cls, request: APIRequest, obj: SpecialDateCalendar, data: Schema, path: Path) -> None:
        await SpecialDateCalendarManager(await request.future_user).leave(obj)
        return None
