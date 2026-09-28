from typing import Type

from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.models.special_date_calendar import SpecialDateCalendar
from special_dates.views.calendar_views.special_date_calendar_action_view import SpecialDateCalendarActionView


class SpecialDateCalendarPreferencesSchema(Schema):
    hide_from_upcoming: bool


class UpdateSpecialDateCalendarPreferencesView(SpecialDateCalendarActionView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return SpecialDateCalendarPreferencesSchema

    @classmethod
    async def run_action(cls, request: APIRequest, obj: SpecialDateCalendar, data: SpecialDateCalendarPreferencesSchema, path: Path) -> None:
        await SpecialDateCalendarManager(await request.future_user).set_hide_from_upcoming(obj, data.hide_from_upcoming)
        return None
